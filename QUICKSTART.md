# FIX FOR: Template Not Found Error

## The Problem
Your Lambda deployment doesn't include the `templates/` folder, causing:
```
jinja2.exceptions.TemplateNotFound: auth.html
```

## Quick Fix (Choose One)

### **If you have Zappa installed** (Easiest):

1. Edit `zappa_settings.json` and set your `s3_bucket`
2. Run:
   ```bash
   zappa deploy prod
   ```
   or on Windows: `deploy.bat`

### **If deploying manually via AWS Console**:

1. Create the ZIP properly:
   ```bash
   # Windows PowerShell
   .\deploy.ps1
   ```
   Or use the batch file: `deploy_manual.bat`

2. Upload `deployment.zip` to Lambda

3. Set handler to: `app.app`

4. Set environment variables from your `.env` file

### **If using Serverless Framework**:

1. Create `serverless.yml` (see DEPLOYMENT.md)
2. Run `sls deploy`

---

## Verify Templates Are Included

Before deploying, check:
```bash
python verify_package.py
```

Or check your ZIP:
```bash
unzip -l deployment.zip | grep templates
```

Should show `templates/auth.html` and `templates/index.html`

---

## Files Created for You

- `zappa_settings.json` - Zappa deployment config (includes templates)
- `.zappaignore` - Files to exclude from deployment
- `deploy.bat` - Windows batch script for Zappa
- `deploy.sh` - Shell script for Zappa
- `deploy.ps1` - PowerShell script to create proper ZIP
- `verify_package.py` - Check if templates are included
- `DEPLOYMENT.md` - Full deployment guide
- `MANIFEST.in` - Ensures templates in Python packages

---

## What to do NOW:

1. **Choose your deployment method**:
   - Zappa? → Edit `zappa_settings.json`, set S3 bucket, run `zappa deploy prod`
   - Manual ZIP? → Run `.\deploy.ps1` to create proper deployment.zip, then upload
   - Serverless? → Create `serverless.yml`, run `sls deploy`

2. **Test** after deploying:
   - Check CloudWatch logs for: `[CONFIG] ✓ Found templates at: /var/task/templates`
   - Visit your app URL

3. **If still failing**, run `python verify_package.py` and share output

---

## Need Help?

Read `DEPLOYMENT.md` for detailed instructions on all deployment methods.
