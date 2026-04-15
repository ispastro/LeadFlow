# Email Notification Testing Guide

## Prerequisites

Before testing, configure email in `.env`:

```bash
# For Gmail (easiest for testing)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=noreply@yourcompany.com
NOTIFICATION_EMAILS=your-email@gmail.com
DASHBOARD_URL=http://localhost:3001
```

**Get Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Enable 2FA if not already enabled
3. Generate app password for "Mail"
4. Copy 16-character password (no spaces)

---

## Method 1: Test Script (Fastest)

Test email service directly without starting server:

```bash
cd backend
python scripts/test_email.py
```

**Expected Output:**
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

**Check your inbox** - you should receive email with:
- Subject: "🎯 New Lead Captured: John Doe"
- Hot lead badge
- Test lead details
- Link to conversation

---

## Method 2: Live Chat Test (Most Realistic)

Test the full flow through chat widget:

### Step 1: Start Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 2: Open Chat Widget
```bash
cd frontend/widget
npm run dev
```

Open http://localhost:3000

### Step 3: Trigger Lead Capture

**Chat conversation:**
```
You: Hi, I'm interested in your services
Bot: [responds]
You: My email is test@example.com
Bot: [captures lead]
```

**Check backend logs:**
```
INFO: Starting email send for lead_id=1
INFO: Email sent successfully in 0.52s
```

**Check inbox** - email should arrive within 2 seconds

---

## Method 3: API Test with cURL

Test the chat endpoint directly:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My email is john@example.com",
    "session_id": "test-session-123",
    "user_email": "john@example.com",
    "user_name": "John Doe"
  }'
```

**Expected Response:**
```json
{
  "response": "Thanks John! I've got your email...",
  "session_id": "test-session-123",
  "lead_captured": true,
  "should_capture_lead": false
}
```

**Check inbox** - email should arrive

---

## Method 4: Python Integration Test

Create automated test:

```python
# tests/test_email_integration.py
import asyncio
from app.services.email_service import email_service

async def test_background_email():
    """Test email sends in background"""
    print("Testing background email...")
    
    # Simulate what happens in chat endpoint
    lead_data = {
        "lead_email": "test@example.com",
        "lead_name": "Test User",
        "intent": "Pricing inquiry",
        "quality": "warm",
        "conversation_id": 1,
        "lead_id": 1
    }
    
    # This would normally be in background task
    email_service.send_lead_notification(**lead_data)
    
    print("Email sent! Check inbox.")

if __name__ == "__main__":
    asyncio.run(test_background_email())
```

Run:
```bash
python tests/test_email_integration.py
```

---

## Method 5: Check Email Without Sending

Verify configuration without actually sending:

```python
# scripts/check_email_config.py
from app.services.email_service import email_service

print("Email Configuration:")
print(f"  Enabled: {email_service.enabled}")
print(f"  SMTP Host: {email_service.smtp_host}:{email_service.smtp_port}")
print(f"  From: {email_service.from_email}")
print(f"  To: {email_service.notification_recipients}")

if email_service.enabled:
    print("\n[OK] Email service is configured correctly!")
else:
    print("\n[X] Email service is NOT configured")
    print("Missing: SMTP_USER, SMTP_PASSWORD, or NOTIFICATION_EMAILS")
```

---

## Troubleshooting

### Issue: "Email service not configured"

**Check .env file:**
```bash
# Windows
type backend\.env | findstr SMTP

# Should show:
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=xxxx...
# NOTIFICATION_EMAILS=your-email@gmail.com
```

**Verify environment variables loaded:**
```python
import os
from dotenv import load_dotenv
load_dotenv()

print(os.getenv("SMTP_USER"))  # Should print your email
print(os.getenv("NOTIFICATION_EMAILS"))  # Should print recipient
```

### Issue: "Authentication failed"

**Gmail:**
- Use App Password, NOT regular password
- Enable 2FA first
- Generate new App Password at https://myaccount.google.com/apppasswords

**SendGrid:**
- Use "apikey" as username
- Use API key as password
- Verify sender email in SendGrid dashboard

### Issue: "Connection timeout"

**Check firewall:**
```bash
# Test SMTP connection
telnet smtp.gmail.com 587
```

**Try alternative port:**
```bash
SMTP_PORT=465  # SSL instead of TLS
```

### Issue: Email sends but not received

**Check spam folder** - first emails often go to spam

**Verify recipient email:**
```bash
# Check for typos
echo $NOTIFICATION_EMAILS
```

**Check email logs:**
```python
# Add to email_service.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Issue: "Background task not executing"

**Check if server is running:**
```bash
curl http://localhost:8000/health
```

**Check logs for errors:**
```bash
# Backend should show:
INFO: Starting email send for lead_id=X
INFO: Email sent successfully in X.XXs
```

**Verify BackgroundTasks imported:**
```python
# In chat.py
from fastapi import BackgroundTasks  # Must be imported
```

---

## Monitoring in Production

### Add Logging

```python
# app/services/email_service.py
import logging
logger = logging.getLogger(__name__)

def send_lead_notification(...):
    logger.info(f"Sending email for lead_id={lead_id}")
    try:
        # send email
        logger.info(f"Email sent to {self.notification_recipients}")
    except Exception as e:
        logger.error(f"Email failed: {e}", exc_info=True)
```

### Track Metrics

```python
# Count emails sent
email_sent_counter = 0

def send_lead_notification(...):
    global email_sent_counter
    email_sent_counter += 1
    logger.info(f"Total emails sent: {email_sent_counter}")
```

### Health Check Endpoint

```python
# app/api/health.py
@router.get("/health/email")
def email_health():
    return {
        "enabled": email_service.enabled,
        "smtp_host": email_service.smtp_host,
        "recipients": len(email_service.notification_recipients)
    }
```

Test:
```bash
curl http://localhost:8000/health/email
```

---

## Quick Checklist

Before going live, verify:

- [ ] `.env` has SMTP credentials
- [ ] `python scripts/test_email.py` succeeds
- [ ] Test email received in inbox
- [ ] Live chat triggers email
- [ ] Email arrives within 5 seconds
- [ ] "View Conversation" link works
- [ ] Email not in spam folder
- [ ] Multiple recipients work (if configured)
- [ ] Backend logs show success
- [ ] No errors in console

---

## Next Steps

Once testing passes:

1. **Update recipients** - Add real sales team emails
2. **Configure production SMTP** - Use SendGrid/AWS SES
3. **Monitor delivery** - Check logs daily
4. **Set up alerts** - Get notified of email failures
5. **Test spam score** - Use mail-tester.com

---

## Support

If issues persist:

1. Check backend logs: `tail -f logs/app.log`
2. Test SMTP directly: `telnet smtp.gmail.com 587`
3. Verify credentials: `python scripts/check_email_config.py`
4. Review EMAIL_SETUP.md for provider-specific guides
