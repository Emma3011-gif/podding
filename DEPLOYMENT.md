# Deployment Guide - Flask PDF Q&A App

## Problem: Templates Not Found

The error `jinja2.exceptions.TemplateNotFound: auth.html` occurs because the `templates/` folder is missing from your AWS Lambda deployment package.

## Solution

### Option 1: Deploy with Zappa (Recommended - Easiest)

1. **Install Zappa**:
   ```bash
   pip install zappa
   ```

2. **Edit `zappa_settings.json`**:
   - Set your `s3_bucket` value to an existing S3 bucket
   - If you don't have an S3 bucket, create one first:
     ```bash
     aws s3 mb s3://your-app-zappa-deployments
     ```

3. **Initial deployment**:
   ```bash
   # On Windows, use:
   deploy.bat

   # Or manually:
   zappa deploy prod
   ```

4. **Update after changes**:
   ```bash
   zappa update prod
   ```

**Important**: The `zappa_settings.json` configuration already includes:
```json
"include": [
  "templates/**",
  "static/**",
  "app.py",
  "auth_integration.py",
  "models.py"
]
```
This ensures templates are packaged.

---

### Option 2: Manual ZIP Deployment (AWS Console)

1. **Create the ZIP package** with the correct structure:

   From your project root, run:
   ```bash
   # Clean first
   rm -f deployment.zip

   # Create ZIP with templates at root level
   cd "C:\Users\user\Desktop\work"
   zip -r deployment.zip ^
     app.py ^
     auth_integration.py ^
     models.py ^
     requirements.txt ^
     templates\ ^
     static\ ^
     data\ 2>nul
   ```

   **Or manually create the ZIP**:
   - Select these items in Explorer:
     - `app.py`
     - `auth_integration.py`
     - `models.py`
     - `requirements.txt`
     - `templates/` folder (entire folder)
     - `static/` folder (entire folder)
   - Right-click → Send to → Compressed (zipped) folder
   - Rename to `deployment.zip`

2. **Verify the ZIP structure**:
   ```bash
   unzip -l deployment.zip
   ```
   Should show:
   ```
   app.py
   auth_integration.py
   models.py
   requirements.txt
   templates/auth.html
   templates/index.html
   static/...
   ```

3. **Upload to AWS Lambda**:
   - Go to AWS Lambda Console
   - Create new function or select existing
   - Code → Upload from → .zip file
   - Upload `deployment.zip`
   - Set handler to `app.app` (if your Flask app variable is named `app`)
   - Runtime: Python 3.11 (or 3.10, 3.9)

4. **Set environment variables** in Lambda Configuration:
   ```
   ENV = production
   DEBUG_AUTH = false
   OPENROUTER_API_KEY = your_key_here
   OPENROUTER_MODEL = openai/gpt-4o-mini
   GOOGLE_CLIENT_ID = your_id
   GOOGLE_CLIENT_SECRET = your_secret
   DATABASE_URL = your_database_url
   ```

5. **Test**:
   - Click "Test" in Lambda console with event `{}`
   - Check logs for: `[CONFIG] ✓ Found templates at: /var/task/templates`
   - Access your API Gateway URL to verify

---

### Option 3: Serverless Framework

If using Serverless Framework (`serverless.yml`):

```yaml
service: pdf-qa-app

provider:
  name: aws
  runtime: python3.11
  environment:
    ENV: production
    DEBUG_AUTH: false
    # Add other env vars...

functions:
  app:
    handler: app.app
    events:
      - http: ANY /
      - http: 'ANY {proxy+}'

package:
  include:
    - templates/**
    - static/**
    - "*.py"
    - requirements.txt
    - MANIFEST.in
  exclude:
    - tests/**
    - .git/**
    - __pycache__/**
    - venv/**
```

Deploy:
```bash
npm install -g serverless
sls deploy
```

---

### Option 4: Docker Provider (Custom Container)

Create `Dockerfile`:

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Copy application code
COPY app.py auth_integration.py models.py requirements.txt ./
COPY templates/ ./templates/
COPY static/ ./static/

# Install dependencies
RUN pip install -r requirements.txt

# Set the CMD to your handler
CMD ["app.app"]
```

Build and push:
```bash
docker build -t pdf-qa-app .
docker tag pdf-qa-app:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/pdf-qa-app:latest
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/pdf-qa-app:latest
```

Then create Lambda from image.

---

## Verifying Templates Are Included

### Check before deploying:

**ZIP file**:
```bash
unzip -l deployment.zip | grep templates
```
Should output lines showing `templates/auth.html` and `templates/index.html`.

**Zappa build**:
After `zappa package prod`, check the `.zappa/` directory:
```bash
ls -la .zappa/**/templates/
```

### Check after deploying:

1. **Check CloudWatch logs** for your Lambda:
   ```bash
   zappa tail prod
   ```
   Or in AWS Console → CloudWatch → Log groups → `/aws/lambda/your-function-name`

   Look for:
   ```
   [CONFIG] ✓ Found templates at: /var/task/templates
   [CONFIG] Templates found: ['auth.html', 'index.html']
   ```

2. **Visit the debug endpoint** (if `DEBUG_AUTH=true`):
   ```
   https://your-api-url/debug/templates
   ```

---

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| `templates/` folder missing in ZIP | Ensure you select the folder itself, not just files inside it |
| `templates/` nested inside another folder in ZIP | ZIP contents must be at root, not `myproject/templates/` |
| Template folder found but no `.html` files | Verify `auth.html` and `index.html` exist locally |
| Using wrong handler name | Handler should be `app.app` (file:function) |
| Dependencies missing | Include `requirements.txt` and ensure all packages are installed before packaging |

---

## File Structure in ZIP/Lambda

```
deployment.zip
├── app.py                    # Main Flask app
├── auth_integration.py       # Auth routes
├── models.py                 # Database models
├── requirements.txt          # Dependencies
├── MANIFEST.in              # Ensures non-Python files included
│
├── templates/               # ← CRITICAL: Must exist!
│   ├── auth.html
│   └── index.html
│
├── static/                 # Optional but needed
│   └── ...
└── data/                  # Optional (if using)
```

---

## Need Help?

1. Run the diagnostic endpoint: `GET /debug/templates` (with `DEBUG_AUTH=true`)
2. Check CloudWatch logs for the config detection output
3. Share the diagnostics if you need further assistance

---

**Quick Start** (if using Zappa):
```bash
# 1. Install zappa
pip install zappa

# 2. Set your S3 bucket in zappa_settings.json

# 3. Deploy
zappa deploy prod
```

That's it! Zappa handles the packaging automatically with the `include` directive.
