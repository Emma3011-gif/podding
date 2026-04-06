"""
Vercel Deployment Debug Checklist
Run this to verify your configuration before deploying
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("VERCEL DEPLOYMENT DEBUG CHECKLIST")
print("=" * 70)

# 1. Check required files exist
print("\n1. Checking required files...")
required_files = [
    'vercel.json',
    'api/index.py',
    'app.py',
    'models.py',
    'requirements.txt',
    'runtime.txt',
    '.env'
]

for f in required_files:
    exists = Path(f).exists()
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status} {f}")

missing_files = [f for f in required_files if not Path(f).exists()]
if missing_files:
    print(f"\n[ERROR] Missing files: {', '.join(missing_files)}")
    print("These are required for Vercel deployment!")
else:
    print("\n[OK] All required files present")

# 2. Check vercel.json is valid JSON
print("\n2. Checking vercel.json syntax...")
try:
    import json
    with open('vercel.json', 'r') as f:
        config = json.load(f)
    print("  [OK] vercel.json is valid JSON")

    # Check required fields
    required_fields = ['version', 'builds', 'routes']
    for field in required_fields:
        if field in config:
            print(f"  [OK] Has '{field}' field")
        else:
            print(f"  [ERROR] Missing '{field}' field")

    # Check builds configuration
    if 'builds' in config:
        for i, build in enumerate(config['builds']):
            if build.get('use') == '@vercel/python':
                print(f"  [OK] Build {i} uses @vercel/python")
            if 'src' in build:
                print(f"  [INFO] Build source: {build['src']}")

except json.JSONDecodeError as e:
    print(f"  [ERROR] Invalid JSON: {e}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 3. Check that api/index.py exists and can import app
print("\n3. Checking api/index.py...")
if Path('api/index.py').exists():
    print("  [OK] api/index.py exists")
    try:
        # Test import
        sys.path.insert(0, str(Path.cwd()))
        from api import index
        print("  [OK] api/index.py imports successfully")
        if hasattr(index, 'app'):
            print("  [OK] 'app' object is exposed")
        else:
            print("  [WARN] 'app' object not found in api/index")
    except Exception as e:
        print(f"  [ERROR] Failed to import api/index.py: {e}")
else:
    print("  [ERROR] api/index.py not found")

# 4. Check requirements.txt formatting
print("\n4. Checking requirements.txt...")
if Path('requirements.txt').exists():
    with open('requirements.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    print(f"  [INFO] Found {len(lines)} dependencies")

    # Check for common issues
    has_pypdf2 = any('PyPDF2' in line for line in lines)
    has_flask = any('flask' in line.lower() for line in lines)
    has_psycopg2 = any('psycopg2' in line.lower() for line in lines)

    if has_pypdf2:
        print("  [OK] PyPDF2 is listed")
    else:
        print("  [WARN] PyPDF2 not found in requirements (may be needed)")

    if has_flask:
        print("  [OK] Flask is listed")
    else:
        print("  [ERROR] Flask not found - required!")

    if has_psycopg2:
        print("  [OK] psycopg2-binary is listed")
    else:
        print("  [WARN] psycopg2-binary not found (needed for PostgreSQL)")

else:
    print("  [ERROR] requirements.txt not found")

# 5. Check environment variables needed for Vercel
print("\n5. Environment Variables Checklist for Vercel:")
print("  You MUST set these in Vercel Dashboard → Settings → Environment Variables:")
print("  [REQUIRED] DATABASE_URL = your Neon PostgreSQL connection string")
print("  [REQUIRED] OPENROUTER_API_KEY = your OpenRouter key")
print("  [REQUIRED] SECRET_KEY = random 64-char hex string")
print("  [REQUIRED] GOOGLE_CLIENT_ID = from Google Cloud Console")
print("  [REQUIRED] GOOGLE_CLIENT_SECRET = from Google Cloud Console")
print("  [OPTIONAL] BLOB_READ_WRITE_TOKEN = for avatar persistence")
print("  [OPTIONAL] ENV = production")
print("\n  Also add this redirect URI in Google Cloud Console:")
print("  https://your-app.vercel.app/auth/google/callback")

# 6. Check for potential runtime issues
print("\n6. Checking for potential runtime issues...")
try:
    # Import app to check for syntax errors
    print("  Testing app import...")
    from app import app as flask_app
    print("  [OK] app.py imports without syntax errors")

    # Check if Flask app has secret key configured
    if flask_app.secret_key:
        print("  [OK] Flask app has secret_key configured")
    else:
        print("  [WARN] Flask app secret_key is not set")

except ImportError as e:
    print(f"  [ERROR] Import error: {e}")
    print("  This could be due to missing dependencies or circular imports")
except Exception as e:
    print(f"  [ERROR] Error importing app: {e}")

# 7. Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
If your Vercel deployment shows FUNCTION_INVOCATION_FAILED:

1. Check Vercel Dashboard → Functions → Logs for the actual error message
2. Ensure ALL required environment variables are set
3. Verify the build succeeded (not just the deployment)
4. Check that requirements.txt includes all dependencies
5. Make sure vercel.json references correct file (api/index.py)

Most common causes:
- Missing DATABASE_URL → app crashes trying to connect
- Missing OPENROUTER_API_KEY → OpenRouter init may fail
- Missing SECRET_KEY → sessions won't work (but shouldn't crash)
- PyPDF2 or other deps not installing (check build logs)

Once you've verified all above, redeploy:
  vercel --prod
  or push to GitHub to trigger deployment
""")

print("=" * 70)
