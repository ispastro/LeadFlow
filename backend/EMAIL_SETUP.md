# Email Notification Setup Guide

## Overview
LeadFlow sends instant email notifications when new leads are captured, enabling your sales team to respond within minutes for maximum conversion.

## Features
- ⚡ **Instant Notifications** - Emails sent in background within 1-2 seconds
- 🎨 **Professional HTML Templates** - Beautiful, mobile-responsive design
- 🔥 **Lead Quality Indicators** - Visual badges for Hot/Warm/Cold leads
- 🔗 **Direct Links** - One-click access to full conversation in dashboard
- 📊 **Lead Details** - Name, email, intent, quality, and timestamp
- 🚀 **Non-Blocking** - Uses FastAPI background tasks (no chat delay)

## Quick Setup

### 1. Gmail (Recommended for Testing)

**Enable App Password:**
1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Copy the 16-character password

**Configure .env:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=noreply@yourcompany.com
NOTIFICATION_EMAILS=sales@yourcompany.com,manager@yourcompany.com
DASHBOARD_URL=http://localhost:3001
```

### 2. SendGrid (Production)

**Setup:**
1. Sign up at https://sendgrid.com (Free: 100 emails/day)
2. Create API Key → Settings → API Keys
3. Verify sender email

**Configure .env:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=verified@yourcompany.com
NOTIFICATION_EMAILS=sales@yourcompany.com
DASHBOARD_URL=https://dashboard.yourcompany.com
```

### 3. AWS SES (Enterprise)

**Setup:**
1. AWS Console → SES → Verify domain/email
2. Create SMTP credentials
3. Move out of sandbox mode for production

**Configure .env:**
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
SMTP_FROM_EMAIL=noreply@yourcompany.com
NOTIFICATION_EMAILS=sales@yourcompany.com
DASHBOARD_URL=https://dashboard.yourcompany.com
```

## Configuration Options

### Multiple Recipients
Comma-separated list (no spaces):
```bash
NOTIFICATION_EMAILS=sales@company.com,manager@company.com,ceo@company.com
```

### Custom From Address
```bash
SMTP_FROM_EMAIL=leadflow@yourcompany.com
```

### Dashboard URL
Used for "View Conversation" button links:
```bash
# Development
DASHBOARD_URL=http://localhost:3001

# Production
DASHBOARD_URL=https://dashboard.yourcompany.com
```

## Email Template

The notification includes:
- **Subject**: "🎯 New Lead Captured: [Name/Email]"
- **Quality Badge**: 🔥 Hot / ⚡ Warm / ❄️ Cold
- **Lead Details**: Name, Email, Intent, Timestamp
- **CTA Button**: Direct link to conversation in dashboard
- **Pro Tip**: "Respond within 5 minutes to increase conversion by 21x"

## Testing

### 1. Test Email Configuration
```python
# Create test script: scripts/test_email.py
from app.services.email_service import email_service

email_service.send_lead_notification(
    lead_email="test@example.com",
    lead_name="Test Lead",
    intent="Enterprise Plan",
    quality="hot",
    conversation_id=1,
    lead_id=1
)
print("Test email sent!")
```

Run:
```bash
python scripts/test_email.py
```

### 2. Test via Chat Widget
1. Start backend: `uvicorn main:app --reload`
2. Open chat widget
3. Provide email when prompted
4. Check inbox for notification

## Troubleshooting

### No Emails Received

**Check logs:**
```bash
# Look for email service warnings/errors
tail -f logs/app.log
```

**Verify configuration:**
```python
# In Python console
from app.services.email_service import email_service
print(f"Enabled: {email_service.enabled}")
print(f"Recipients: {email_service.notification_recipients}")
```

### Gmail "Less Secure Apps" Error
- Use App Password (not regular password)
- Enable 2FA first
- Generate new App Password

### SendGrid Not Sending
- Verify sender email in SendGrid dashboard
- Check API key permissions
- Review SendGrid activity logs

### AWS SES Sandbox Mode
- Verify all recipient emails in SES console
- Request production access to send to any email

## Production Best Practices

### 1. Use Dedicated Email Service
- Gmail: Max 500 emails/day (not recommended for production)
- SendGrid: 100/day free, scalable paid plans
- AWS SES: $0.10 per 1,000 emails

### 2. Monitor Delivery
- Enable bounce/complaint handling
- Track open rates (optional)
- Set up alerts for failed sends

### 3. Rate Limiting
Current implementation has no rate limiting. For high-volume:
```python
# Add to email_service.py
from time import sleep
sleep(0.1)  # 10 emails/second max
```

### 4. Retry Logic
Add retry for transient failures:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def send_lead_notification(...):
    # existing code
```

## Disable Notifications

To disable without removing code:
```bash
# Leave SMTP_USER empty or remove it
SMTP_USER=
```

Service will log warning but continue working:
```
WARNING: Email service not configured - skipping notification
```

## Alternative: Webhook Notifications

For Slack/Discord/Teams integration, add webhook support:

```python
# app/services/webhook_service.py
import httpx

async def send_slack_notification(lead_data):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json={
            "text": f"🎯 New Lead: {lead_data['email']}"
        })
```

Add to background tasks in chat.py:
```python
background_tasks.add_task(send_slack_notification, lead_data)
```

## Support

For issues:
1. Check logs for error messages
2. Verify SMTP credentials
3. Test with simple SMTP client first
4. Review provider-specific documentation
