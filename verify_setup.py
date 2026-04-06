"""
Comprehensive verification that the app is properly configured for Neon PostgreSQL + Google OAuth
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("NEON POSTGRES + GOOGLE OAUTH SETUP VERIFICATION")
print("=" * 60)

# Step 1: Check .env exists and load it
env_path = Path('.') / '.env'
if not env_path.exists():
    print("[ERROR] .env file not found!")
    sys.exit(1)

load_dotenv(dotenv_path=env_path)
print("[OK] .env file loaded")

# Step 2: Check required environment variables
required_vars = {
    'DATABASE_URL': 'Neon PostgreSQL connection string',
    'OPENROUTER_API_KEY': 'OpenRouter API key',
    'SECRET_KEY': 'Flask session secret',
    'GOOGLE_CLIENT_ID': 'Google OAuth client ID',
    'GOOGLE_CLIENT_SECRET': 'Google OAuth client secret',
}

print("\nChecking environment variables:")
for var, desc in required_vars.items():
    val = os.getenv(var)
    if val:
        print(f"  [OK] {var}: {'*' * min(20, len(val))} (length={len(val)})")
    else:
        print(f"  [ERROR] {var}: NOT SET ({desc})")
        print(f"           Please add {var} to your .env file")

missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print(f"\n[ERROR] Missing required variables: {', '.join(missing)}")
    sys.exit(1)

# Step 3: Test database connection
print("\nTesting database connection:")
try:
    import psycopg2
    DATABASE_URL = os.getenv('DATABASE_URL')

    # Mask password in output
    if '@' in DATABASE_URL:
        parts = DATABASE_URL.split('@')
        user_pass = parts[0].split('://')[1]
        username, password = user_pass.split(':', 1)
        masked = f"{DATABASE_URL.split('://')[0]}://{username}:{'*' * len(password)}@{parts[1]}"
        print(f"  Connecting to: {masked}")

    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    cur = conn.cursor()

    # Test query
    cur.execute('SELECT version()')
    version = cur.fetchone()
    print(f"  [OK] Connected to PostgreSQL")
    print(f"  [INFO] Version: {version[0][:60]}...")

    # Check database name
    cur.execute('SELECT current_database()')
    db_name = cur.fetchone()[0]
    print(f"  [INFO] Database: {db_name}")

    conn.close()
except Exception as e:
    print(f"  [ERROR] Database connection failed: {e}")
    sys.exit(1)

# Step 4: Test models module
print("\nTesting models module:")
try:
    # Import after env is loaded
    from importlib import reload
    import models
    reload(models)  # Ensure fresh import
    print(f"  [OK] models imported")
    print(f"  [INFO] DB_TYPE: {models.DB_TYPE}")

    # Check tables exist
    conn = models.get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    print(f"  [INFO] Existing tables: {', '.join(tables)}")

    required_tables = ['users', 'documents', 'chat_messages', 'embeddings']
    missing_tables = [t for t in required_tables if t not in tables]
    if missing_tables:
        print(f"  [WARN] Missing tables: {', '.join(missing_tables)}")
        print("          Run: python setup_database.py")
    else:
        print(f"  [OK] All required tables exist")
    conn.close()
except Exception as e:
    print(f"  [ERROR] Models test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Check Google OAuth configuration
print("\nChecking Google OAuth configuration:")
client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

if client_id and client_secret:
    print(f"  [OK] GOOGLE_CLIENT_ID: {client_id[:30]}...")
    print(f"  [OK] GOOGLE_CLIENT_SECRET: {'*' * min(20, len(client_secret))}")

    # Check redirect URI format
    print("\n  Important: In Google Cloud Console, configure these redirect URIs:")
    print("    [LOCAL]  http://localhost:5000/auth/google/callback")
    print("    [PROD]   https://your-app.vercel.app/auth/google/callback")
    print("  Make sure to replace 'your-app' with your actual Vercel domain.")
else:
    print("  [ERROR] Google OAuth credentials not fully set")
    sys.exit(1)

# Step 6: Check Flask app
print("\nTesting Flask app import:")
try:
    from app import app
    print(f"  [OK] Flask app imported")
    print(f"  [INFO] Secret key: {'[SET]' if app.secret_key else '[NOT SET]'}")

    # Check app configuration
    print(f"  [INFO] Template folder: {app.template_folder}")
    print(f"  [INFO] Static folder: {app.static_folder}")
except Exception as e:
    print(f"  [ERROR] Failed to import Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE - ALL CHECKS PASSED!")
print("=" * 60)
print("\nNext steps:")
print("1. Start the app: python app.py")
print("2. Open browser: http://localhost:5000")
print("3. Click 'Sign up with Google' to test OAuth")
print("4. After successful auth, you'll be redirected to the app")
print("5. Check Neon database: users table should have your record")
print("\nFor Vercel deployment:")
print("  - Push to GitHub")
print("  - Import repository in Vercel")
print("  - Set all environment variables in Vercel")
print("  - Deploy")
