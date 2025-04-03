import os
import sys
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import AdminUser, db

# Admin user creation script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    # Create Flask app context to interact with the database
    app = Flask(__name__)
    
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
    
    # Initialize the database with the app
    db.init_app(app)
    
    with app.app_context():
        # Check if the admin already exists
        existing_admin = AdminUser.query.filter_by(username=username).first()
        password_hash = generate_password_hash(password)
        
        try:
            if existing_admin:
                # Update existing admin password
                existing_admin.password_hash = password_hash
                db.session.commit()
                print(f"Admin user '{username}' password updated successfully!")
            else:
                # Create a new admin user
                admin_user = AdminUser(username=username, password_hash=password_hash)
                db.session.add(admin_user)
                db.session.commit()
                print(f"Admin user '{username}' created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error: Failed to create admin user: {str(e)}")
            sys.exit(1)