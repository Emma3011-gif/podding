# 🚀 START HERE - Quick Deployment Guide

**Problem**: `jinja2.exceptions.TemplateNotFound: auth.html`
**Root Cause**: Templates folder missing from deployment package
**Solution**: Use manual ZIP upload to AWS Lambda (no S3 needed, completely free)

---

## ⚡ 3-Step Solution

### **Step 1: Create Deployment ZIP**

Open **PowerShell** in this folder and run:

```powershell
.\deploy.ps1
```

Expected output:
```
✓ Templates/auth.html: FOUND
✓ Templates/index.html: FOUND
✓ ZIP is ready for deployment!
```

This creates `deployment.zip`.

---

### **Step 2: Deploy to AWS Lambda**

1. Go to https://console.aws.amazon.com/lambda/
2. Click **"Create function"**
3. Fill in:
   - Function name: `pdf-qa-app`
   - Runtime: **Python 3.11**
   - Architecture: **x86_64**
4. Click **"Create function"**

---

### **Step 3: Configure & Upload**

**A. Upload Code:**
- Code tab → Upload from → `.zip file`
- Select `deployment.zip`
- Wait for upload

**B. Set Handler:**
- Runtime settings → Edit
- Handler: `app.app`
- Save

**C. Add Environment Variables:**
- Configuration → Environment variables → Edit
- Copy all variables from your `.env` file
- At minimum:
  ```
  ENV = production
  OPENROUTER_API_KEY = your_key_here
  OPENROUTER_MODEL = openai/gpt-4o-mini
  DATABASE_URL = your_database_url
  ```
- Save

**D. Increase Timeout:**
- Configuration → General configuration → Edit
- Timeout: 30 seconds
- Memory: 512 MB (or 1024 MB)
- Save

---

### **Step 4: Make It Publicly Accessible**

- In your Lambda, click **"Add trigger"**
- Choose: **API Gateway**
- API type: **HTTP API**
- Security: **Open**
- Click **"Add"**
- Copy the API endpoint URL

---

### **Step 5: Test**

1. Open the API endpoint URL in browser
2. Should see authentication page
3. Try signing up and using the app

**Check logs** (Monitor → View logs in CloudWatch) for:
```
[CONFIG] ✓ Found templates at: /var/task/templates
```

---

## 📁 Files Created for You

| File | Purpose |
|------|---------|
| `deploy.ps1` | Creates deployment ZIP with correct structure |
| `verify_package.py` | Check if templates are included |
| `README-MANUAL-DEPLOY.md` | Detailed deployment instructions |
| `DEPLOYMENT-CHECKLIST.md` | Step-by-step checklist |
| `MANIFEST.in` | Ensures templates in Python packages |
| `app.py` (updated) | Robust template detection |
| `auth_integration.py` (updated) | Helpful error messages if templates missing |

---

## 🔄 Updating Your App

When you make code changes:

```powershell
.\deploy.ps1
```

Then in AWS Lambda:
- Code tab → Upload new `deployment.zip`

Or use AWS CLI:
```bash
aws lambda update-function-code --function-name pdf-qa-app --zip-file fileb://deployment.zip
```

---

## 🆘 Troubleshooting

**Still seeing "Template not found"?**
1. Re-run `.\deploy.ps1` (do not manually create ZIP)
2. Upload the new `deployment.zip`
3. Check CloudWatch logs for the template detection messages

**Error: "Handler not found"**
- Handler must be exactly `app.app`

**Error: "No module named flask"**
- `requirements.txt` must be in ZIP at root level
- Recreate ZIP with `deploy.ps1`

**Lambda times out**
- Increase timeout to 60 seconds
- Increase memory to 1024 MB

---

## 💰 Cost

AWS Free Tier:
- Lambda: 1,000,000 requests/month FREE
- API Gateway: 1,000,000 requests/month FREE
- Data transfer: 100 GB/month FREE

**You can stay entirely within free tier** for a personal/hobby app.

---

## Need Help?

1. Check **CloudWatch logs** for your Lambda function
2. Look for `[CONFIG] ✓ Found templates` message
3. Read **README-MANUAL-DEPLOY.md** for detailed instructions
4. Use **DEPLOYMENT-CHECKLIST.md** to verify each step

---

**Ready?** Run `.\deploy.ps1` and then create your Lambda function!
