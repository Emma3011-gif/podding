# PDF Q&A Assistant with Authentication

A modern, professional web application for uploading PDFs and having natural conversations about their contents using AI, with user authentication.

## Features

- **Secure Authentication**: Email/password signup & login with session management
- **Social Login**: Google OAuth integration ready
- **Multiple Document Types**: Upload PDFs, DOCX, and images (JPG/PNG/WebP/BMP) (max 25MB)
- **OCR for Images**: Extract text from images using Tesseract OCR
- **Smart Q&A**: AI-powered question answering using semantic search with embeddings
- **Simple Explanations**: AI automatically breaks down complex concepts into easy-to-understand language with real-world examples
- **Quiz Generation**: Generate knowledge-check quizzes on demand to reinforce learning
- **Streaming Responses**: Real-time streaming chat responses
- **Session Persistence**: Auto-save and restore conversations after page refresh
- **Human-like Greetings**: AI responds to greetings naturally like a real person
- **Professional UI**: Clean, responsive design with avatars, justified text, smooth animations
- **Conversation Memory**: AI remembers the full conversation history
- **Fast Performance**: Optimized chunking, caching, and configurable settings

## Quick Start (Simplified - Recommended)

### Prerequisites

- Python 3.9+
- pip package manager
- OpenRouter API key (free signup at https://openrouter.ai)

### 1. Install Python Dependencies

```bash
cd C:\Users\user\Desktop\work
pip install -r requirements.txt
```

### 2. Install System Dependencies (Optional)

**For image OCR (JPG/PNG/etc):**
- Install **Tesseract OCR** on your system:
  - **Windows**: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
  - **macOS**: `brew install tesseract`
  - **Linux**: `sudo apt install tesseract-ocr`
- If Tesseract is not in your PATH, set `TESSERACT_CMD` in `.env` to the full executable path.

**Note**: OCR is optional; the app works without it but image files will not be supported.

### 3. Configure API Key

1. Get your OpenRouter API key: https://openrouter.ai/api-keys
2. Edit the `.env` file (created from `.env.example` if needed):

```env
OPENROUTER_API_KEY=sk-or-your-actual-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini  # Fast and affordable
ENV=development  # or "production" for deployment

# Optional: Tesseract executable path if not in system PATH
# TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe  # (Windows example)
```

**Optional - Google OAuth**: To enable "Sign up with Google", also add:

```env
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```
Follow the setup instructions in the "Google OAuth Setup" section below.

### 4. Run with Authentication

```bash
python app_unified.py
```

Open your browser: **http://localhost:5000**

You'll first see the **signup/login screen**. Create an account to access the PDF Q&A app.

---

## Authentication Setup

### Overview

The app includes a complete authentication system:

1. **Sign up** with email & password (display name required)
2. **Log in** with email & password
3. **Social login** buttons ready (Google) - requires OAuth setup
4. **Session management** via Flask sessions
5. **Route protection** - only authenticated users can access the main app

### Files

- `templates/auth.html` - Authentication UI (React + Tailwind)
- `auth_integration.py` - Backend auth routes and helpers
- `app_unified.py` - Main app (integrates auth)

### How It Works

1. User visits `/` → checks if authenticated
   - ✅ Yes → redirects to main app
   - ❌ No → redirects to `/auth` (shows signup/login form)

2. After signup/login:
   - Session created with user_id, email, display_name
   - Redirected to main app (`/`)
   - Can now upload PDFs and chat

3. Session persists across page refreshes
4. Logout clears session

### Adding Authentication to Your App

The unified app already includes authentication! Just:

1. Import the auth blueprint in `app_unified.py`:

```python
from auth_integration import auth_bp, login_required

# Add after app initialization:
app.register_blueprint(auth_bp)

# Protect your main route:
@app.route('/')
@login_required
def index():
    return render_template('index.html')
```

2. Run the app and visit `/` - you'll be redirected to `/auth` first

3. After signing up, you'll be redirected back to the main app

### Disabling Authentication (Optional)

If you don't want auth, comment out in `app_unified.py`:

```python
# app.register_blueprint(auth_bp)  # Comment out

# Remove @login_required from index route
@app.route('/')
def index():
    return render_template('index.html')
```

---

## Google OAuth Setup (Optional)

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Google+ API" (or "Google OAuth2 API")
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Web application**
6. Authorized redirect URIs:
   - For local development: `http://localhost:5000/auth/google/callback`
   - For production: `https://yourdomain.com/auth/google/callback`
7. Click **Create** and copy your:
   - **Client ID** → `GOOGLE_CLIENT_ID`
   - **Client Secret** → `GOOGLE_CLIENT_SECRET`

### Step 2: Configure Environment Variables

Add to your `.env` file:

```env
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Step 3: How It Works

- Users click **"Continue with Google"** on the auth page
- They're redirected to Google to authorize
- After approval, they're redirected back to your app
- Account is automatically created (if first time) or logged in
- Redirected to main app with session established

### Troubleshooting Google OAuth

- **"redirect_uri_mismatch"**: Ensure the redirect URI in Google Console exactly matches `http://localhost:5000/auth/google/callback` (or your production URL)
- **Missing scopes**: The app requests `openid email profile` scopes automatically
- **User not created**: Check server logs for errors during OAuth callback

---

---

## Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | OpenRouter API key from https://openrouter.ai/api-keys |
| `OPENROUTER_MODEL` | No | `openai/gpt-4o-mini` | AI model to use |
| `ENV` | No | `development` | `development` (debug) or `production` |
| `CHUNK_SIZE` | No | `1000` | PDF text chunk size (characters) |
| `TOP_K_RESULTS` | No | `3` | Number of context chunks to include |
| `GOOGLE_CLIENT_ID` | No (for Google OAuth) | - | Google OAuth client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | No (for Google OAuth) | - | Google OAuth client secret from Google Cloud Console |

### Popular AI Models

Change `OPENROUTER_MODEL` in `.env`:

| Model ID | Speed | Quality | Recommendation |
|----------|-------|---------|----------------|
| `openai/gpt-4o-mini` | ⚡⚡⚡ | Good | ✅ **Default - Best value** |
| `anthropic/claude-3-haiku` | ⚡⚡ | Excellent | ✅ Great for Q&A |
| `openai/gpt-4o` | ⚡ | Excellent | ✅ High quality |
| `stepfun/step-3.5-flash:free` | 🐢 | Fair | ⚠️ Free but slow |

See all: https://openrouter.ai/models

---

## Project Structure

```
.
├── app_unified.py       # Main Flask app (frontend + backend + auth)
├── auth_integration.py  # Authentication routes and helpers
├── templates/
│   ├── auth.html        # Modern signup/login page (React + Tailwind)
│   └── index.html       # Main PDF Q&A interface
├── static/
│   ├── style.css        # Professional styling for main app
│   └── script.js        # Frontend JavaScript
├── requirements.txt
├── .env                 # Your configuration (DO NOT COMMIT)
├── .env.example
├── README.md
├── PERFORMANCE.md       # Performance optimization guide
├── MIGRATION.md         # OpenAI to OpenRouter migration
└── *.bak                # Legacy files (backend.py, app.py, etc.)
```

---

## Usage

### First Time

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure**: Edit `.env` with your OpenRouter API key
3. **Run**: `python app_unified.py`
4. **Visit**: http://localhost:5000 → You'll see the auth screen
5. **Create account**: Fill in your details, accept terms
6. **Start using**: Upload PDFs, chat with AI

### Sign Up

1. Enter your display name
2. Enter your email
3. Create a password (min 6 characters)
4. Accept Terms of Use and Privacy Policy
5. Click "Sign up with Email"
6. You'll be redirected to the main app

### Log In

1. Click "Log in" on the auth screen
2. Enter email and password
3. Click "Log in"
4. Access your PDF Q&A workspace

### Using the App

- **Upload a PDF** (drag & drop or click)
- **Ask questions** about the document
- **Chat naturally** - AI responds conversationally
- **Refresh page** - session persists, chat history restored

### Logout

Currently, logout functionality is in the API only. To add a logout button in the UI, you can add it to the main app header:

```javascript
// In static/script.js
function logout() {
    fetch('/auth/logout', { method: 'POST' })
        .then(() => window.location.href = '/auth');
}
```

---

## Customization

### Styling the Auth Page

Edit `templates/auth.html`:
- Colors: Update Tailwind config at the top (brand colors)
- Logo: Change gradient colors in `.gradient-text` class
- Fonts: Change Inter to another Google Font
- Layout: Modify Tailwind classes for container

### Form Fields

Add more fields in `templates/auth.html` and update `auth_integration.py`:
- In the signup form, add new InputField components
- In `/signup` endpoint, handle the new fields
- Update USERS dict structure

### Password Hashing (Production)

In `auth_integration.py`, replace plain text storage:

```python
import bcrypt

# During signup:
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
USERS[email]['password'] = hashed

# During login:
if not bcrypt.checkpw(password.encode(), user['password']):
    return jsonify({'error': 'Invalid credentials'}), 401
```

---

## Security Notes

⚠️ **For Development/Prototype Only**

This auth system is **not production-ready** without:

1. **Password hashing** (use bcrypt or Argon2)
2. **Database** (use PostgreSQL/SQLite instead of USERS dict)
3. **HTTPS** (always use TLS in production)
4. **CSRF protection** (Flask-WTF or similar)
5. **Rate limiting** (prevent brute force)
6. **Secure session secret** (set SECRET_KEY env var)
7. **Email verification** (verify email before account activation)
8. **Password reset** flow
9. **JWT tokens** for stateless auth (optional)

For production, consider:
- Auth0, Firebase Auth, Supabase Auth (managed services)
- Flask-Login or Flask-Security for session management
- SQLAlchemy for database ORM

---

## Troubleshooting

### "Redirect loop"
Make sure you're not redirecting from `/auth` to `/` then back to `/auth` in a cycle. Check the `index()` route has `@login_required`.

### "Session not persisting"
- Check Flask `SECRET_KEY` is set (app generates one automatically)
- Ensure browser cookies are enabled
- Check session storage in DevTools > Application

### "Auth page shows blank"
Open browser console (F12) → check for JavaScript errors. Make sure React CDN loaded correctly.

### "Social login does nothing"
Social login is a placeholder. You need to implement OAuth flows in `auth_integration.py`.

---

## Production Deployment

### AWS Lambda (Manual ZIP - Recommended, No S3 Needed)

**Completely free within AWS free tier. No S3 bucket required.**

1. **Prepare your environment**: Fill in `.env` with your API keys and database URL

2. **Create deployment package**:
   ```powershell
   # On Windows, run PowerShell script
   .\deploy.ps1
   ```
   This creates `deployment.zip` with correct structure.

3. **Create Lambda function**:
   - Go to AWS Lambda Console
   - Click "Create function"
   - Runtime: Python 3.11
   - Create new role with basic permissions

4. **Upload code**:
   - Code → Upload from → .zip file
   - Select `deployment.zip`
   - Handler: `app.app`

5. **Configure**:
   - Add environment variables from `.env`
   - Timeout: 30 seconds
   - Memory: 512 MB (1024 recommended)

6. **Add API Gateway trigger** to make it accessible via HTTP

7. **Test**: Visit the API Gateway URL

For detailed step-by-step instructions, see **`README-MANUAL-DEPLOY.md`**.

---

### Alternative: Local Development Server

For testing locally:
```bash
pip install -r requirements.txt
python app.py
```
Visit: http://localhost:5000/auth/

---

### Other Platforms

- **Vercel / Railway / PythonAnywhere**: Not natively supported for this Flask app. Use AWS Lambda or self-host.
- **Docker**: See `DOCKER.md` (if available)

See `PERFORMANCE.md` for performance tuning tips.

---

## License

Free to use.

---

## Getting Help

- **OpenRouter Docs**: https://openrouter.ai/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **React**: https://react.dev

---

**Ready to use?** Run `python app_unified.py` and go to http://localhost:5000!
