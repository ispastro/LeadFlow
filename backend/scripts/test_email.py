"""
Test email notification system
Run: python scripts/test_email.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.email_service import email_service
from dotenv import load_dotenv

load_dotenv()


def test_email_notification():
    """Send test email notification"""
    # Configure from settings
    from config import settings
    email_service.configure(settings)
    
    print("Testing email notification system...")
    print(f"SMTP Host: {email_service.smtp_host}")
    print(f"SMTP Port: {email_service.smtp_port}")
    print(f"From Email: {email_service.from_email}")
    print(f"Recipients: {email_service.notification_recipients}")
    print(f"Enabled: {email_service.enabled}")
    print()
    
    if not email_service.enabled:
        print("[X] Email service not configured!")
        print("Please set SMTP_USER, SMTP_PASSWORD, and NOTIFICATION_EMAILS in .env")
        print("\nExample configuration:")
        print("  SMTP_USER=your-email@gmail.com")
        print("  SMTP_PASSWORD=your-app-password")
        print("  NOTIFICATION_EMAILS=sales@company.com")
        return
    
    print("Sending test notification...")
    
    try:
        email_service.send_lead_notification(
            lead_email="john.doe@example.com",
            lead_name="John Doe",
            intent="Enterprise Plan - AI Automation",
            quality="hot",
            conversation_id=999,
            lead_id=999
        )
        print("[OK] Test email sent successfully!")
        print(f"Check inbox: {', '.join(email_service.notification_recipients)}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_email_notification()
