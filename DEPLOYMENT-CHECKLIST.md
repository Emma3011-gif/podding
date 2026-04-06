# Deployment Checklist - Manual ZIP Upload

**Target: AWS Lambda + API Gateway (no S3, completely free tier eligible)**

---

## Before You Start

- [ ] AWS account created (https://console.aws.amazon.com/)
- [ ] Project folder ready with all files
- [ ] `.env` file filled with your API keys and database URL

---

## Phase 1: Create Deployment Package

- [ ] Open PowerShell in project folder
- [ ] Run: `.\deploy.ps1`
- [ ] Verify output:
  - ✓ Templates/auth.html: FOUND
  - ✓ Templates/index.html: FOUND
- [ ] `deployment.zip` file created

---

## Phase 2: Create Lambda Function

- [ ] Go to AWS Lambda Console
- [ ] Click "Create function"
- [ ] Name: `pdf-qa-app`
- [ ] Runtime: **Python 3.11**
- [ ] Architecture: **x86_64**
- [ ] Create new role (default)
- [ ] Click "Create function"

---

## Phase 3: Upload Code

- [ ] In Code tab, click "Upload from" → ".zip file"
- [ ] Select `deployment.zip`
- [ ] Wait for upload
- [ ] Verify files appear in editor (app.py, templates/, etc.)

---

## Phase 4: Configure Handler

- [ ] In Code tab, find "Runtime settings"
- [ ] Click "Edit"
- [ ] Handler: `app.app`
- [ ] Click "Save"

---

## Phase 5: Set Environment Variables

- [ ] Go to Configuration → Environment variables → Edit
- [ ] Add all variables from `.env`:
  - `ENV` = `production`
  - `DEBUG_AUTH` = `false`
  - `OPENROUTER_API_KEY` = your key
  - `OPENROUTER_MODEL` = `openai/gpt-4o-mini`
  - `GOOGLE_CLIENT_ID` = your id (if using)
  - `GOOGLE_CLIENT_SECRET` = your secret (if using)
  - `DATABASE_URL` = your database URL
- [ ] Click "Save"

---

## Phase 6: Increase Resources

- [ ] Configuration → General configuration → Edit
- [ ] Timeout: **30 seconds** (or 60)
- [ ] Memory: **512 MB** (or 1024 MB)
- [ ] Click "Save"

---

## Phase 7: Add API Gateway

- [ ] In Function overview, click "Add trigger"
- [ ] Choose: **API Gateway**
- [ ] API type: **HTTP API** (cheaper) or REST API
- [ ] Security: **Open**
- [ ] Click "Add"
- [ ] Copy the API endpoint URL (looks like: `https://xyz.execute-api.region.amazonaws.com/`)

---

## Phase 8: Test Deployment

- [ ] Go to Monitor → View logs in CloudWatch
- [ ] Check for:
  - `[CONFIG] ✓ Found templates at: /var/task/templates`
  - `[CONFIG] Templates found: ['auth.html', 'index.html']`
- [ ] Open API endpoint URL in browser
- [ ] Should see authentication page
- [ ] Try signing up / logging in
- [ ] Test PDF upload and Q&A

---

## If Something Goes Wrong

| Issue | Fix |
|-------|-----|
| Template not found | Re-run `deploy.ps1` and upload fresh ZIP. Check ZIP structure. |
| Handler not found | Handler must be `app.app` exactly |
| Missing modules | Check `requirements.txt` is in ZIP. Recreate ZIP. |
| 502 Bad Gateway | Check CloudWatch logs for errors, increase timeout to 60s |
| 403/401 on API | Ensure API Gateway trigger added and security=Open |

**Check CloudWatch logs** → Look for errors starting with `[ERROR]` or `[WARN]`

---

## That's It!

Your app is now running on AWS Lambda with a free tier.

**To update later**: Run `deploy.ps1` again and upload new `deployment.zip`.

**To monitor**: CloudWatch logs → Log group `/aws/lambda/pdf-qa-app`
