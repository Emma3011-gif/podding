"""
Authentication Integration for Flask PDF Q&A App

This module provides:
1. Auth routes (login, signup, logout, Google OAuth)
2. Middleware to protect routes
3. Session management helpers

Database-backed user storage (using models.py)
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from authlib.integrations.flask_client import OAuth
from authlib.common.errors import AuthlibBaseError
from jinja2.exceptions import TemplateNotFound
import uuid
import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

# Import database models
try:
    from models import create_user, get_user_by_email, get_user_by_id, update_user_avatar, save_avatar
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Failed to import models: {e}")
    MODELS_AVAILABLE = False

# Load environment variables from the project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize OAuth
oauth = OAuth()
oauth_configured = False

# Debug flag
DEBUG_AUTH = os.getenv('DEBUG_AUTH', 'false').lower() == 'true'


def init_oauth(app):
    """Initialize OAuth with the Flask app"""
    global oauth_configured
    oauth_configured = False
    oauth.init_app(app)

    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if google_client_id and google_client_secret:
        try:
            oauth.register(
                name='google',
                client_id=google_client_id,
                client_secret=google_client_secret,
                server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                access_token_url='https://oauth2.googleapis.com/token',
                authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
                api_base_url='https://www.googleapis.com/oauth2/v2/',
                userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
                client_kwargs={'scope': 'openid email profile'},
            )
            oauth_configured = True
            print("[OK] Google OAuth configured")

            with app.app_context():
                try:
                    redirect_uri = url_for('auth.google_callback', _external=True)
                    print(f"[INFO] Expected Google OAuth redirect URI: {redirect_uri}")
                    print("[IMPORTANT] Add this exact URI to your Google Cloud Console")
                except Exception as e:
                    print(f"[WARN] Could not generate redirect URI: {e}")

        except Exception as e:
            print(f"[ERROR] Failed to register Google OAuth: {e}")
            import traceback
            traceback.print_exc()
            oauth_configured = False
    else:
        missing = []
        if not google_client_id:
            missing.append('GOOGLE_CLIENT_ID')
        if not google_client_secret:
            missing.append('GOOGLE_CLIENT_SECRET')
        print(f"[WARN] Google OAuth not configured (missing: {', '.join(missing)})")
        oauth_configured = False


@auth_bp.route('/google')
def google_login():
    """Initiate Google OAuth flow"""
    if not oauth_configured:
        error_msg = "Google OAuth is not configured. Please check server configuration and environment variables."
        print(f"[ERROR] {error_msg}")
        return redirect(url_for('auth.auth_page', error=error_msg))

    try:
        if DEBUG_AUTH:
            print("[DEBUG] Google login initiated")
        redirect_uri = url_for('auth.google_callback', _external=True)
        if DEBUG_AUTH:
            print(f"[DEBUG] Redirect URI: {redirect_uri}")
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Google OAuth initialization error: {type(e).__name__}: {e}")
        print(error_details)
        error_msg = f'Google OAuth initialization failed: {type(e).__name__}'
        if DEBUG_AUTH:
            error_msg += f' - {str(e)}'
        else:
            error_msg += '. Please try again or use email/password login.'
        return redirect(url_for('auth.auth_page', error=error_msg))


@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    if not oauth_configured:
        error_msg = "Google OAuth is not configured. Please check server configuration."
        print(f"[ERROR] {error_msg}")
        return redirect(url_for('auth.auth_page', error=error_msg))

    try:
        if DEBUG_AUTH:
            print(f"[DEBUG] Google callback received")
            print(f"[DEBUG] Request args: {request.args}")

        if 'error' in request.args:
            error = request.args.get('error')
            error_description = request.args.get('error_description', '')
            error_msg = f"Google OAuth error: {error}"
            if error_description:
                error_msg += f" - {error_description}"
            print(f"[ERROR] {error_msg}")
            return redirect(url_for('auth.auth_page', error=error_msg))

        if 'code' not in request.args:
            msg = "Missing authorization code in callback. This may indicate an incomplete OAuth flow. Please try logging in again."
            print(f"[ERROR] {msg} Request args: {request.args}")
            return redirect(url_for('auth.auth_page', error=msg))

        try:
            if DEBUG_AUTH:
                print(f"[DEBUG] Attempting to exchange code for token")
            token = oauth.google.authorize_access_token()
            if DEBUG_AUTH:
                print(f"[DEBUG] Token obtained successfully")
            if not token:
                msg = "Google returned an empty token response. This may indicate a misconfiguration."
                print(f"[ERROR] {msg}")
                return redirect(url_for('auth.auth_page', error=msg))
        except requests.RequestException as e:
            msg = f"Network error connecting to Google: {type(e).__name__}. Please check your internet connection and firewall settings."
            print(f"[ERROR] {msg} - {e}")
            return redirect(url_for('auth.auth_page', error=msg))
        except AuthlibBaseError as e:
            error_str = str(e).lower()
            if 'invalid_grant' in error_str:
                if 'state' in error_str or 'csrf' in error_str:
                    msg = "CSRF state validation failed. This usually happens if cookies are disabled or if you opened the login link in a new tab. Please ensure cookies are enabled and try again in the same browser window."
                else:
                    msg = "The authorization code has expired or is invalid. Please try logging in again. If the problem persists, check that your system clock is correct."
            elif 'invalid_client' in error_str:
                msg = "Client authentication failed. Your GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET may be incorrect, or the OAuth consent screen is not properly configured."
            elif 'unauthorized_client' in error_str:
                msg = "This client is not authorized to request an authorization code. Check your Google Cloud Console OAuth client settings."
            elif 'redirect_uri_mismatch' in error_str:
                msg = "Redirect URI mismatch. The callback URL does not match any registered URIs in your Google Cloud Console."
            else:
                msg = f"OAuth token exchange failed: {str(e)}"
            print(f"[ERROR] {msg}")
            return redirect(url_for('auth.auth_page', error=msg))
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[ERROR] Unexpected error during token exchange:")
            print(f"[ERROR] Exception type: {type(e).__name__}")
            print(f"[ERROR] Exception message: {e}")
            print(f"[ERROR] Traceback:\n{error_details}")
            msg = f'Failed to obtain access token: {type(e).__name__}'
            if DEBUG_AUTH:
                msg += f': {str(e)}'
            return redirect(url_for('auth.auth_page', error=msg))

        user_info = token.get('userinfo')
        if not user_info:
            msg = "Google did not return user profile information. This may indicate insufficient OAuth scopes or an account issue."
            print(f"[ERROR] {msg}, token keys: {list(token.keys()) if token else 'None'}")
            return redirect(url_for('auth.auth_page', error=msg))

        email = user_info.get('email', '').lower()
        google_id = user_info.get('sub', '')
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')

        if not email:
            error_msg = 'Google authentication failed: No email address was provided. Please ensure your Google account has a verified email.'
            print(f"[ERROR] {error_msg}, user_info_keys: {list(user_info.keys())}")
            return redirect(url_for('auth.auth_page', error=error_msg))

        # Check if user exists in database
        user = None
        if MODELS_AVAILABLE:
            user = get_user_by_email(email)

        if not user:
            # New user - create in database
            user_id = str(uuid.uuid4())
            if MODELS_AVAILABLE:
                create_user(
                    user_id=user_id,
                    email=email,
                    google_id=google_id,
                    display_name=name
                )
                print(f"[INFO] New user created in DB via Google OAuth: {email}")

                # Optionally download Google avatar
                if picture:
                    try:
                        import requests
                        from io import BytesIO
                        from PIL import Image
                        resp = requests.get(picture, timeout=5)
                        if resp.status_code == 200:
                            img = Image.open(BytesIO(resp.content))
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            img = img.resize((200, 200), Image.Resampling.LANCZOS)
                            # Encode image to JPEG bytes
                            buffer = BytesIO()
                            img.save(buffer, format='JPEG')
                            avatar_filename = save_avatar(user_id, buffer.getvalue(), 'avatar.jpg')
                            update_user_avatar(user_id, avatar_filename)
                            print(f"[INFO] Saved Google avatar for {email}")
                    except Exception as e:
                        print(f"[WARN] Failed to download Google avatar: {e}")
        else:
            # Existing user - update Google info if needed
            if MODELS_AVAILABLE:
                updated = False
                if not user.get('google_id'):
                    # This shouldn't happen in current schema but let's be safe
                    # We'd need an update_user_google_id function - skipping for now
                    pass
                if not user.get('display_name') and name:
                    # Update display name if missing
                    from models import update_user_name
                    update_user_name(user['id'], name)
                    updated = True
                if updated:
                    print(f"[INFO] Updated existing user via Google OAuth: {email}")
                user = get_user_by_id(user['id'])  # Refresh user data

        # Create session
        if user:
            session['user_id'] = user['id']
            session['user_email'] = email
            session['user_name'] = user.get('display_name', name)
        else:
            # Fallback if DB failed
            session['user_id'] = str(uuid.uuid4())
            session['user_email'] = email
            session['user_name'] = name

        # Redirect to home page
        return redirect(url_for('index'))

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Unexpected error in Google callback:")
        print(error_details)
        error_msg = f'Google authentication failed: {type(e).__name__}'
        if DEBUG_AUTH:
            error_msg += f' - {str(e)}'
        else:
            error_msg += '. Please try again or use email/password login.'
        return redirect(url_for('auth.auth_page', error=error_msg))


@auth_bp.route('/')
def auth_page():
    """Render the authentication page"""
    if session.get('user_id'):
        return redirect(url_for('index'))

    try:
        return render_template('auth.html')
    except TemplateNotFound:
        # Provide detailed error information for debugging
        import os
        from flask import current_app

        template_folder = current_app.template_folder
        template_path = os.path.join(template_folder, 'auth.html')

        error_details = {
            'error': 'Template not found',
            'template_folder': template_folder,
            'folder_exists': os.path.exists(template_folder),
            'auth_html_exists': os.path.exists(template_path),
            'folder_contents': os.listdir(template_folder) if os.path.exists(template_folder) else 'FOLDER MISSING',
            'cwd': os.getcwd(),
            'base_dir': os.path.dirname(os.path.abspath(__file__))
        }

        # Log detailed error
        print(f"[ERROR] Template render failed:")
        print(f"  Template folder: {template_folder}")
        print(f"  Folder exists: {error_details['folder_exists']}")
        print(f"  auth.html exists: {error_details['auth_html_exists']}")
        print(f"  Contents: {error_details['folder_contents']}")

        # Return a user-friendly error page with technical details
        return f"""
        <h1>Configuration Error</h1>
        <p>The authentication page could not be loaded because the template file is missing.</p>
        <h2>Diagnostics:</h2>
        <pre>{error_details}</pre>
        <h2>Fix:</h2>
        <p>Ensure your deployment includes the <code>templates/auth.html</code> file at the correct location.</p>
        <p>The application checked: <code>{template_folder}</code></p>
        """, 500


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Handle user signup"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Invalid request: Content-Type must be application/json'}), 400

        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'error': 'Invalid request: Malformed JSON or empty body'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        display_name = data.get('displayName', '').strip()

        if not email or not password or (not display_name and 'displayName' in data):
            return jsonify({'error': 'All fields are required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if user exists in database
        if MODELS_AVAILABLE:
            existing_user = get_user_by_email(email)
            if existing_user:
                return jsonify({'error': 'An account with this email already exists'}), 400
        else:
            # Fallback if DB not available - but should not happen
            return jsonify({'error': 'Database not available'}), 500

        # Create user in database with hashed password
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        if MODELS_AVAILABLE:
            create_user(
                user_id=user_id,
                email=email,
                password_hash=password_hash,
                display_name=display_name
            )
        else:
            return jsonify({'error': 'Database not available'}), 500

        # Create session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = display_name

        print(f"[INFO] New user signed up: {email}")
        return jsonify({'success': True, 'message': 'Account created successfully'})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Signup error: {type(e).__name__}: {e}")
        print(error_details)
        error_msg = f'An error occurred during signup: {type(e).__name__}: {str(e)}'
        return jsonify({'error': error_msg}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Invalid request: Content-Type must be application/json'}), 400

        data = request.get_json(silent=True)
        if data is None:
            return jsonify({'error': 'Invalid request: Malformed JSON or empty body'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Check credentials in database
        if MODELS_AVAILABLE:
            user = get_user_by_email(email)
            if not user:
                return jsonify({'error': 'Invalid email or password'}), 401

            # Verify password (if user has a password hash - they might be OAuth-only)
            if user.get('password_hash'):
                if not check_password_hash(user['password_hash'], password):
                    return jsonify({'error': 'Invalid email or password'}), 401
            else:
                # User might have signed up with Google only
                return jsonify({'error': 'Invalid email or password'}), 401
        else:
            return jsonify({'error': 'Database not available'}), 500

        # Create session
        session['user_id'] = user['id']
        session['user_email'] = email
        session['user_name'] = user['display_name']

        print(f"[INFO] User logged in: {email}")
        return jsonify({'success': True, 'message': 'Logged in successfully'})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Login error: {type(e).__name__}: {e}")
        print(error_details)
        error_msg = 'An error occurred during login'
        if DEBUG_AUTH:
            error_msg += f' ({type(e).__name__}: {str(e)})'
        return jsonify({'error': error_msg}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    session.clear()
    print("[INFO] User logged out")
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@auth_bp.route('/check')
def check_auth():
    """Check if user is authenticated"""
    if session.get('user_id'):
        return jsonify({
            'authenticated': True,
            'user': {
                'email': session.get('user_email'),
                'name': session.get('user_name'),
                'id': session.get('user_id')
            }
        })
    return jsonify({'authenticated': False}), 401


@auth_bp.route('/debug/oauth-config')
def debug_oauth_config():
    """Debug endpoint to show OAuth configuration (only if DEBUG_AUTH is true)"""
    if not DEBUG_AUTH:
        return jsonify({'error': 'Debug endpoint disabled'}), 403

    try:
        redirect_uri = url_for('auth.google_callback', _external=True)
        return jsonify({
            'debug': True,
            'redirect_uri': redirect_uri,
            'client_id_set': bool(os.getenv('GOOGLE_CLIENT_ID')),
            'client_secret_set': bool(os.getenv('GOOGLE_CLIENT_SECRET')),
            'instructions': [
                f"Add this redirect URI to Google Cloud Console:",
                redirect_uri,
                "",
                "Steps:",
                "1. Go to https://console.cloud.google.com/apis/credentials",
                "2. Click on your OAuth 2.0 Client ID",
                "3. Under 'Authorized redirect URIs', add the URI above",
                "4. Save changes"
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Helper function to protect routes
def login_required(view_func):
    """
    Decorator to protect routes that require authentication.

    Usage:
        @app.route('/chat')
        @login_required
        def chat():
            return render_template('chat.html')
    """
    from functools import wraps

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            accept_header = request.headers.get('Accept', '')
            is_html_request = 'text/html' in accept_header

            if is_html_request:
                return redirect(url_for('auth.auth_page'))
            else:
                return jsonify({'error': 'Authentication required', 'code': 'auth_required'}), 401
        return view_func(*args, **kwargs)

    return wrapped_view
