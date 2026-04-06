"""Test Neon database connection"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
load_dotenv('.env')
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env")
    exit(1)

# Mask password for display
masked = DATABASE_URL
if '@' in DATABASE_URL:
    before_at = DATABASE_URL.split('@')[0]
    if ':' in before_at:
        user_pass = before_at.split('://')[1]
        if ':' in user_pass:
            username, password = user_pass.split(':', 1)
            masked = f"{DATABASE_URL.split('://')[0]}://{username}:{'*' * len(password)}@{DATABASE_URL.split('@')[1]}"

print(f"DATABASE_URL: {masked}")

# Test connection
print("\nTesting connection to Neon...")
try:
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    print("[SUCCESS] Connected to Neon PostgreSQL!")

    # Check database info
    cur = conn.cursor()
    cur.execute("SELECT version()")
    version = cur.fetchone()
    print(f"[INFO] PostgreSQL version: {version[0][:50]}...")

    cur.execute("SELECT current_database()")
    db_name = cur.fetchone()[0]
    print(f"[INFO] Connected to database: {db_name}")

    cur.close()
    conn.close()

    print("\n✓ Your credentials are correct and working!")

except psycopg2.OperationalError as e:
    print(f"\n[ERROR] Connection failed: {e}")
    if "password authentication failed" in str(e):
        print("\n🔍 Root cause: Password is incorrect")
        print("\n📋 How to fix:")
        print("1. Go to https://neon.tech")
        print("2. Select your project: ep-super-cake-a4uqwgdu")
        print("3. Click 'Connection Details' in the left sidebar")
        print("4. Click 'Show password' to reveal the password")
        print("5. Copy the ENTIRE connection string")
        print("6. Update .env with the new DATABASE_URL")
        print("\n⚠️  Note: Neon may have rotated your password. Click 'Reset password' if needed.")
    elif "could not connect to server" in str(e):
        print("\n🔍 Root cause: Cannot reach the server")
        print("  - Check your internet connection")
        print("  - Neon may be blocking your IP (check Neon dashboard for connection limits)")
    else:
        print("\n🔍 Unknown operational error")
except ImportError:
    print("[ERROR] psycopg2 is not installed. Run: pip install psycopg2-binary")
except Exception as e:
    print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
