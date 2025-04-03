import os
import logging
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from search_engine import (
    search_all_engines, 
    get_available_engines, 
    search_all_image_engines,
    get_available_image_engines
)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure the database
db_user = os.environ.get("PGUSER")
db_password = os.environ.get("PGPASSWORD")
db_host = os.environ.get("PGHOST")
db_port = os.environ.get("PGPORT")
db_name = os.environ.get("PGDATABASE")

# Build the database URL
database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database
db = SQLAlchemy(app)

# Make the model circular import work
import models

# Create tables
with app.app_context():
    db.create_all()

# In-memory cache for search results
# Format: {query: {'results': [...], 'timestamp': time.time()}}
search_cache = {}

@app.route('/')
def index():
    """Render the main search page"""
    engines = get_available_engines()
    return render_template('index.html', engines=engines)

@app.route('/search')
def search():
    """Handle search requests and render results page"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    # Get selected engines from query params or use all available
    engines = request.args.getlist('engines') or get_available_engines()
    
    if not query:
        return render_template('index.html', engines=get_available_engines())
    
    # Record this search in the database
    try:
        search_record = models.SearchHistory(
            query=query,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            engines=','.join(engines) if engines else None
        )
        db.session.add(search_record)
        db.session.commit()
        logger.debug(f"Recorded search: '{query}'")
    except Exception as e:
        logger.error(f"Failed to record search: {str(e)}")
        db.session.rollback()
    
    # Render the results page (actual results will be loaded via AJAX)
    return render_template('results.html', 
                          query=query, 
                          page=page, 
                          selected_engines=engines,
                          all_engines=get_available_engines())

@app.route('/api/search')
def api_search():
    """API endpoint to get search results"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    # Get selected engines from query params or use all available
    engines = request.args.getlist('engines') or get_available_engines()
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Check cache first
        cache_key = f"{query}:{','.join(sorted(engines))}:{page}"
        if cache_key in search_cache:
            logger.debug(f"Returning cached results for '{query}'")
            return jsonify(search_cache[cache_key])
        
        # If not in cache, perform the search
        results = search_all_engines(query, engines, page)
        
        # Update search history with results count if we have any results
        if 'web_results' in results and results['web_results']:
            try:
                # Find the most recent search with this query
                recent_search = db.session.query(models.SearchHistory)\
                    .filter_by(query=query)\
                    .order_by(models.SearchHistory.timestamp.desc())\
                    .first()
                    
                if recent_search:
                    recent_search.results_count = len(results['web_results'])
                    db.session.commit()
            except Exception as e:
                logger.error(f"Failed to update results count: {str(e)}")
                db.session.rollback()
                
        # Cache the results
        search_cache[cache_key] = results
        
        # Clean up cache if it gets too large (simple strategy)
        if len(search_cache) > 100:
            # Just remove the oldest entries (first 20)
            keys_to_remove = list(search_cache.keys())[:20]
            for key in keys_to_remove:
                search_cache.pop(key, None)
                
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error searching for '{query}': {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/about')
def about():
    """Render the about me page"""
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html', error="Page not found"), 404

@app.route('/api/image-search')
def api_image_search():
    """API endpoint to get image search results"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Check cache first
        cache_key = f"img:{query}:{page}"
        if cache_key in search_cache:
            logger.debug(f"Returning cached image results for '{query}'")
            return jsonify(search_cache[cache_key])
        
        # If not in cache, perform the image search
        results = search_all_image_engines(query, page=page)
        
        # Cache the results
        search_cache[cache_key] = results
        
        # Clean up cache if it gets too large
        if len(search_cache) > 100:
            keys_to_remove = list(search_cache.keys())[:20]
            for key in keys_to_remove:
                search_cache.pop(key, None)
                
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error searching for images '{query}': {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search-suggestions')
def api_search_suggestions():
    """API endpoint to get search suggestions based on history"""
    query = request.args.get('q', '').lower()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    try:
        # Get the most recent search history entries that start with the query
        # Limit to 5 suggestions
        search_suggestions = db.session.query(models.SearchHistory.query)\
            .filter(models.SearchHistory.query.ilike(f"{query}%"))\
            .group_by(models.SearchHistory.query)\
            .order_by(db.func.count(models.SearchHistory.query).desc())\
            .limit(5)\
            .all()
        
        # Extract just the query strings
        suggestions = [item[0] for item in search_suggestions]
        
        return jsonify(suggestions)
    
    except Exception as e:
        logger.error(f"Error getting search suggestions for '{query}': {str(e)}")
        return jsonify([])



# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Please provide both username and password')
        return render_template('admin_login.html')
    
    admin = db.session.query(models.AdminUser).filter_by(username=username).first()
    
    from werkzeug.security import check_password_hash
    if admin and check_password_hash(admin.password_hash, password):
        session['admin_logged_in'] = True
        session['admin_username'] = admin.username
        return redirect(url_for('admin_dashboard'))
    
    flash('Invalid username or password')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard - requires login"""
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return redirect(url_for('admin_login'))
    
    # Get recent search history
    recent_searches = db.session.query(models.SearchHistory)\
        .order_by(models.SearchHistory.timestamp.desc())\
        .limit(100)\
        .all()
    
    # Get search counts
    search_counts = db.session.query(
        models.SearchHistory.query,
        db.func.count(models.SearchHistory.id).label('count')
    ).group_by(models.SearchHistory.query)\
     .order_by(db.desc('count'))\
     .limit(10)\
     .all()
    
    return render_template(
        'admin_dashboard.html',
        recent_searches=recent_searches,
        search_counts=search_counts
    )

@app.route('/api/admin/clear-history', methods=['POST'])
def api_admin_clear_history():
    """API endpoint to clear search history - requires admin login"""
    if 'admin_logged_in' not in session or not session['admin_logged_in']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        db.session.query(models.SearchHistory).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Search history cleared'})
    except Exception as e:
        logger.error(f"Error clearing search history: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Vercel"""
    return jsonify({"status": "ok"}), 200

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return render_template('index.html', error="An internal server error occurred"), 500
