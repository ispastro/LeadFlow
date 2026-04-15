# Quick Start: Test Email Notifications in 5 Minutes

## Step 1: Check Current Status (30 seconds)

```bash
cd backend
python scripts/check_email_config.py
```

**You'll see:**
- ✅ Enabled = Ready to test
- ❌ Disabled = Need to configure (go to Step 2)

---

## Step 2: Configure Email (2 minutes)

### Option A: Gmail (Easiest)

**Get App Password:**
1. Visit: https://myaccount.google.com/apppasswords
2. Enable 2FA if prompted
3. Create app password for "Mail"
4. Copy 16-character password (e.g., `abcd efgh ijkl mnop`)

**Add to `.env`:**
```bash
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
NOTIFICATION_EMAILS=your-email@gmail.com
DASHBOARD_URL=http://localhost:3001
```

### Option B: SendGrid (Production)

```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
NOTIFICATION_EMAILS=sales@company.com
DASHBOARD_URL=http://localhost:3001
```

---

## Step 3: Verify Configuration (10 seconds)

```bash
python scripts/check_email_config.py
```

**Should show:**
```
[OK] Email service is ENABLED and configured
```

---

## Step 4: Send Test Email (30 seconds)

```bash
python scripts/test_email.py
```

**Expected output:**
```
Testing email notification system...
SMTP Host: smtp.gmail.com
SMTP Port: 587
From Email: noreply@yourcompany.com
Recipients: ['your-email@gmail.com']
Enabled: True

Sending test notification...
[OK] Test email sent successfully!
Check inbox: your-email@gmail.com
```

**Check your inbox** - you should receive:

```
Subject: 🎯 New Lead Captured: John Doe

🔥 HOT LEAD

Name: John Doe
Email: john.doe@example.com
Intent: Enterprise Plan - AI Automation
Captured: [timestamp]

[View Full Conversation →]

💡 Pro Tip: Respond within 5 minutes to increase conversion by 21x
```

---

## Step 5: Test Live (2 minutes)

### Start Backend
```bash
uvicorn main:app --reload --port 8000
```

### Start Chat Widget
```bash
cd ../frontend/widget
npm run dev
```

### Open Browser
Go to http://localhost:3000

### Chat Conversation
```
You: Hi, I'm interested in your AI services
Bot: [responds with info]
You: My email is test@example.com
Bot: [captures lead and sends email]
```

### Check Backend Logs
```
INFO: Starting email send for lead_id=1
INFO: Email sent successfully in 0.52s
```

### Check Inbox
Email should arrive within 2-5 seconds!

---

## Troubleshooting

### "Email service not configured"
- Check `.env` file exists in `backend/` folder
- Verify SMTP_USER, SMTP_PASSWORD, NOTIFICATION_EMAILS are set
- No spaces in values

### "Authentication failed" (Gmail)
- Use App Password, NOT regular password
- Enable 2FA first
- Remove spaces from app password (16 chars)

### "Connection timeout"
- Check internet connection
- Try port 465 instead of 587
- Check firewall settings

### Email not received
- Check spam/junk folder
- Verify recipient email is correct
- Try sending to different email address

---

## What Happens When Lead is Captured?

```
User provides email in chat
         ↓
Backend saves lead to database (10ms)
         ↓
Background task queued (instant)
         ↓
User gets AI response immediately (50ms)
         ↓
[Response sent to user]
         ↓
Background task executes (500ms)
         ↓
Email sent to sales team
         ↓
Sales team gets notification
         ↓
Click "View Conversation" link
         ↓
Opens dashboard with full chat history
```

**Total time from lead capture to email delivery: ~1-2 seconds**

---

## Production Checklist

Before going live:

- [ ] Test email received successfully
- [ ] "View Conversation" link works
- [ ] Email not in spam folder
- [ ] Update NOTIFICATION_EMAILS to real sales team
- [ ] Set DASHBOARD_URL to production domain
- [ ] Consider SendGrid/AWS SES for reliability
- [ ] Monitor backend logs for email failures
- [ ] Test with multiple recipients

---

## Next Steps

**Working?** 
- Update recipients to your sales team emails
- Deploy to production
- Monitor email delivery

**Not working?**
- See TESTING_EMAIL.md for detailed troubleshooting
- Check backend logs for errors
- Verify SMTP credentials

**Want more?**
- Add Slack notifications (see EMAIL_SETUP.md)
- Set up retry logic with Celery
- Add email open tracking
