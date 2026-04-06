"""
Database Setup Script for Neon PostgreSQL
Run this once to create all required tables in your Neon database.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import models to get database connection and init_db
sys.path.insert(0, str(Path(__file__).parent))

# Check if DATABASE_URL is set
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("[ERROR] DATABASE_URL is not set in .env")
    print("Please add your Neon PostgreSQL connection string to .env")
    sys.exit(1)

print(f"[INFO] Connecting to Neon PostgreSQL...")
print(f"[INFO] Database: {DATABASE_URL.split('@')[1].split('/')[1] if '@' in DATABASE_URL else 'Unknown'}")

try:
    # Import models module
    from models import init_db, get_db_connection, DB_TYPE
    print(f"[INFO] Database type: {DB_TYPE}")
    print(f"[INFO] Initializing database schema...")

    # Initialize database (creates all tables)
    init_db()

    print("\n[SUCCESS] Database initialized successfully!")
    print("\nCreated tables:")
    print("  - users (with google_id support)")
    print("  - documents")
    print("  - chat_messages")
    print("  - embeddings")
    print("\nNext steps:")
    print("1. Test the app locally: python app.py")
    print("2. Go to http://localhost:5000")
    print("3. Click 'Sign up with Google' to test OAuth")
    print("\nNote: Make sure your Google OAuth client is configured with:")
    print("  - Authorized redirect URI: http://localhost:5000/auth/google/callback")

except ImportError as e:
    print(f"[ERROR] Failed to import models: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Database initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
