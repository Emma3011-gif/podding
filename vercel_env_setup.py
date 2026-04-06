"""
Vercel Environment Variables Setup Script
Run this to see exactly what values to set in Vercel Dashboard
"""

import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 80)
print("VERCEL ENVIRONMENT VARIABLES SETUP")
print("=" * 80)

# Load local .env
env_path = Path('.') / '.env'
if not env_path.exists():
    print("[ERROR] .env file not found!")
    exit(1)

load_dotenv(env_path)

# Define required variables
required_vars = {
    'DATABASE_URL': {
        'description': 'Neon PostgreSQL connection string',
        'example': 'postgresql://username:password@host/dbname?sslmode=require',
        'required': True
    },
    'OPENROUTER_API_KEY': {
        'description': 'OpenRouter API key for AI chat',
        'example': 'sk-or-v1-...',
        'required': True
    },
    'SECRET_KEY': {
        'description': 'Flask session secret (64-char hex)',
        'example': '0c42b05ef1dd2a807845437caf2dcc35361629c7113a38a5a2cb431becaddca8',
        'required': True
    },
    'GOOGLE_CLIENT_ID': {
        'description': 'Google OAuth client ID',
        'example': '12345678-xxxx.apps.googleusercontent.com',
        'required': True
    },
    'GOOGLE_CLIENT_SECRET': {
        'description': 'Google OAuth client secret',
        'example': 'GOCSPX-....',
        'required': True
    },
    'BLOB_READ_WRITE_TOKEN': {
        'description': 'Vercel Blob Storage token (for avatars)',
        'example': 'vercel_blob_rw_...',
        'required': False  # Optional but recommended
    },
    'ENV': {
        'description': 'Environment mode',
        'example': 'production',
        'required': False,
        'default': 'production'
    }
}

print("\n[INFO] Copy each of these EXACT values into Vercel Dashboard:\n")
print("-" * 80)
print("Vercel Dashboard > Your Project > Settings > Environment Variables")
print("-" * 80)

for key, info in required_vars.items():
    value = os.getenv(key)
    if value:
        print(f"\n[OK] {key}")
        print(f"   Description: {info['description']}")
        print(f"   Value: {value}")
    else:
        print(f"\n[MISSING] {key}")
        print(f"   Description: {info['description']}")
        print(f"   Add to .env: {key}={info['example']}")

print("\n" + "=" * 80)
print("[IMPORTANT] GOOGLE CLOUD CONSOLE - ALSO CONFIGURE THIS:")
print("=" * 80)
print("""
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", ADD:
   https://pdf-assistant-iota.vercel.app/auth/google/callback
4. Save
""")
print("=" * 80)
print("\n[OK] After setting ALL environment variables:")
print("   1. Go to Vercel Deployments")
print("   2. Click '...' on latest deployment")
print("   3. Click 'Redeploy'")
print("   4. Wait and test your app")
print("=" * 80)
