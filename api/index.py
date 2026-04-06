"""
Vercel Serverless Function Entry Point
Wraps the Flask app for Vercel deployment
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the Flask app from app.py
try:
    from app import app as flask_app
except ImportError as e:
    print(f"Error importing Flask app: {e}")
    raise

# Vercel expects the handler to be named "handler" or will use the app directly
# For Flask/WSGI apps, we can expose the app directly
app = flask_app
