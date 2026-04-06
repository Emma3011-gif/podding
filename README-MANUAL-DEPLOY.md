# Manual Deployment to AWS Lambda (ZIP Upload)

**No S3 bucket needed. Completely free within AWS free tier.**

---

## Prerequisites

- AWS account (free tier)
- Python 3.11+ installed locally (for creating ZIP)
- Your project files ready

---

## Step-by-Step Deployment

### **Step 1: Prepare Your Environment Variables**

Create a file named `.env` with your configuration (already exists if you have one). Required variables:

```env
ENV=production
DEBUG_AUTH=false

# Get from https://openrouter.ai/
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openai/gpt-4o-mini

# Google OAuth (optional but set if using)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Database URL (Neon/Supabase/etc.)
DATABASE_URL=postgresql://...
```

**Important**: Never commit `.env` to git (already in `.gitignore`).

---

### **Step 2: Create the Deployment ZIP**

Run the PowerShell script included in this project:

```powershell
# Open PowerShell in the project folder (right-click → "Open in Terminal")
.\deploy.ps1
```

This will:
- Verify templates exist
- Copy all necessary files to a temp folder
- Create `deployment.zip` with correct structure
- Verify the ZIP contents

**Output should show:**
```
✓ ZIP is ready for deployment!
  Templates/auth.html: ✓ FOUND
  Templates/index.html: ✓ FOUND
```

---

### **Step 3: Create the Lambda Function**

1. Go to **AWS Lambda Console**: https://console.aws.amazon.com/lambda/

2. Click **"Create function"**

3. Choose:
   - **Function name**: `pdf-qa-app` (or your preferred name)
   - **Runtime**: Python 3.11 (or 3.10)
   - **Architecture**: x86_64
   - **Permissions**: Create a new role with basic Lambda permissions (default is fine)

4. Click **"Create function"**

---

### **Step 4: Upload the Deployment ZIP**

1. In your new Lambda function, go to the **"Code"** tab

2. Under **"Code source"**, click **"Upload from" → ".zip file"**

3. Click **"Upload"** and select `deployment.zip` from your project folder

4. Wait for upload (~5-10 seconds)

5. Verify the files appear in the code editor (you should see `app.py`, `templates/`, etc.)

---

### **Step 5: Configure the Lambda**

#### **Set Handler**
- In **"Code source"** section, find **"Runtime settings"**
- Click **"Edit"**
- **Handler**: `app.app`
- Click **"Save"**

#### **Add Environment Variables**
- Go to **"Configuration"** tab → **"Environment variables"**
- Click **"Edit"**
- Add all variables from your `.env` file:
  ```
  ENV = production
  DEBUG_AUTH = false
  OPENROUTER_API_KEY = your_key
  OPENROUTER_MODEL = openai/gpt-4o-mini
  GOOGLE_CLIENT_ID = your_id (if using OAuth)
  GOOGLE_CLIENT_SECRET = your_secret (if using OAuth)
  DATABASE_URL = your_database_url
  ```
- Click **"Save"**

#### **Increase Timeout and Memory**
- Go to **"Configuration"** → **"General configuration"**
- Click **"Edit"**
- **Timeout**: 30 seconds (minimum for PDF uploads; increase to 60 if needed)
- **Memory**: 512 MB (minimum) or 1024 MB (recommended for better performance)
- Click **"Save"**

---

### **Step 6: Test the Lambda**

1. Go to **"Test"** tab

2. Create a new test event:
   - **Event name**: `test`
   - Leave JSON as `{}` (or use: `{"queryStringParameters": {}, "body": null}`)
   - Click **"Save"**

3. Click **"Test"** button

4. Check the **Execution result**:
   - **Status**: `200` (success)
   - Output should show your Flask app starting

5. Check **"Execution log"** for these lines:
   ```
   [CONFIG] ✓ Found templates at: /var/task/templates
   [CONFIG] Templates found: ['auth.html', 'index.html']
   ```

   If you see these, templates are correctly deployed!

---

### **Step 7: Add API Gateway (Make it Publicly Accessible)**

1. In your Lambda function, click **"Add trigger"**

2. Choose **"API Gateway"**

3. Configure:
   - **API type**: HTTP API (recommended, cheaper) or REST API
   - **Security**: Open (for now; you can add authorizer later)
   - Click **"Add"**

4. Copy the **API endpoint URL** (looks like: `https://abc123.execute-api.us-east-1.amazonaws.com/`)

5. **Test your app**:
   - Open the URL in browser
   - Should see the authentication page (`/auth/`)
   - Check CloudWatch logs if any errors

---

## Optional: Add a Custom Domain

If you want a nice URL (e.g., `app.yourdomain.com`):

1. In API Gateway, create a **Custom Domain Name**
2. Add a CNAME record in your DNS pointing to the API Gateway domain
3. Update API Gateway to use the custom domain
4. Update Lambda trigger URL accordingly

---

## Updating Your App

When you make code changes:

1. Run `.\deploy.ps1` again (creates new `deployment.zip`)
2. In AWS Lambda Console, go to **"Code"** tab
3. Click **"Upload from" → ".zip file"**
4. Upload the new ZIP
5. Click **"Deploy"** button

Or automate with AWS CLI:
```bash
aws lambda update-function-code \
  --function-name pdf-qa-app \
  --zip-file fileb://deployment.zip
```

---

## Troubleshooting

### **Error: "Handler not found"**
- Handler must be exactly `app.app`
- Check that `app.py` contains a Flask app variable named `app`
- Verify the file structure in ZIP: `app.py` at root, not in a subfolder

### **Error: "Template not found"**
- Check CloudWatch logs for `[CONFIG] template_folder: ...`
- It should say `/var/task/templates`
- If folder is missing, re-run `deploy.ps1` and upload fresh ZIP
- Ensure `templates/` folder exists locally with `auth.html` and `index.html`

### **Error: "No module named 'flask'"**
- Dependencies didn't install
- Lambda uses `requirements.txt` to install on first deploy
- Ensure `requirements.txt` is in ZIP at the root
- Check CloudWatch logs for dependency installation errors
- Recreate ZIP with `deploy.ps1`

### **Slow performance or timeout**
- Increase Lambda timeout (Configuration → General configuration)
- Increase memory to 1024 MB
- Check that OpenRouter API key is valid and not rate-limited

---

## Cost Estimate (AWS Free Tier)

| Service | Free Tier | Estimated Monthly Cost (light usage) |
|---------|-----------|--------------------------------------|
| Lambda | 1M requests, 400,000 GB-s | $0 (if under limits) |
| API Gateway (HTTP) | 1M requests | $0 (if under limits) |
| Data Transfer | 100 GB out | $0 (if under limits) |
| **Total** | | **~$0** for hobby use |

---

## Next Steps

- [ ] Run `.\deploy.ps1` to create ZIP
- [ ] Create Lambda function in AWS Console
- [ ] Upload ZIP
- [ ] Set handler to `app.app`
- [ ] Add environment variables
- [ ] Increase timeout to 30s
- [ ] Add API Gateway trigger
- [ ] Test your app URL
- [ ] Check CloudWatch logs for `[CONFIG] ✓ Found templates`

---

**Need help?** Check CloudWatch logs (Monitor → View logs in CloudWatch) and look for the configuration messages.
