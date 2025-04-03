# Colossus Search Engine

A powerful metasearch engine that aggregates results from multiple search providers including Google, Bing, DuckDuckGo, Yahoo, and Brave Search.

## Features

- Multi-engine search capabilities
- Automatic result aggregation
- AI-powered "Key Insights" summary of search results using OpenAI
- Comprehensive image search from multiple sources
- Clean, responsive user interface
- No tracking or data collection

## Deployment Instructions

### Deploying to Vercel

1. Sign up for a [Vercel account](https://vercel.com/signup) if you don't have one
2. Install the Vercel CLI: `npm i -g vercel`
3. Clone this repository to your local machine
4. Navigate to the project directory
5. Run `vercel` and follow the prompts
6. When asked about build settings, use:
   - Build Command: `pip install -r requirements-vercel.txt`
   - Output Directory: (leave empty)

Alternatively, you can deploy directly from the Vercel dashboard by connecting your GitHub repository.

### Environment Variables

The application needs the following environment variables:

- `SESSION_SECRET`: A random string used for securing the application (optional, but recommended)
- `OPENAI_API_KEY`: Your OpenAI API key for generating AI summaries of search results (required)

## Local Development

1. Install dependencies: `pip install -r requirements-vercel.txt`
2. Run the application: `python main.py`
3. Open your browser and navigate to: `http://localhost:5000`

## Files to Upload

When deploying to Vercel, include:

- All Python files (*.py)
- Templates directory
- Static directory
- vercel.json
- requirements-vercel.txt

## Files to Exclude

The following files are specific to Replit and can be excluded:

- .replit
- replit.nix
- pyproject.toml
- uv.lock
- .config/