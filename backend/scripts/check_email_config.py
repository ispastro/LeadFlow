"""
Check email configuration without sending
Run: python scripts/check_email_config.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.email_service import email_service
from dotenv import load_dotenv

load_dotenv()


def check_config():
    """Check email configuration"""
    # Force reload configuration
    email_service._load_config()
    
    print("=" * 60)
    print("EMAIL CONFIGURATION CHECK")
    print("=" * 60)
    print()
    
    print("Configuration:")
    print(f"  SMTP Host: {email_service.smtp_host}")
    print(f"  SMTP Port: {email_service.smtp_port}")
    print(f"  SMTP User: {email_service.smtp_user or '[NOT SET]'}")
    print(f"  SMTP Password: {'*' * 16 if email_service.smtp_password else '[NOT SET]'}")
    print(f"  From Email: {email_service.from_email or '[NOT SET]'}")
    print(f"  Recipients: {email_service.notification_recipients}")
    print(f"  Dashboard URL: {os.getenv('DASHBOARD_URL', '[NOT SET]')}")
    print()
    
    print("Status:")
    if email_service.enabled:
        print("  [OK] Email service is ENABLED and configured")
        print()
        print("Next steps:")
        print("  1. Run: python scripts/test_email.py")
        print("  2. Check inbox for test email")
        print("  3. Start backend and test via chat widget")
    else:
        print("  [X] Email service is DISABLED")
        print()
        print("Missing configuration:")
        if not email_service.smtp_user:
            print("  - SMTP_USER (your email address)")
        if not email_service.smtp_password:
            print("  - SMTP_PASSWORD (app password or API key)")
        if not email_service.notification_recipients[0]:
            print("  - NOTIFICATION_EMAILS (comma-separated recipients)")
        print()
        print("Quick setup for Gmail:")
        print("  1. Get app password: https://myaccount.google.com/apppasswords")
        print("  2. Add to .env:")
        print("     SMTP_USER=your-email@gmail.com")
        print("     SMTP_PASSWORD=your-16-char-app-password")
        print("     NOTIFICATION_EMAILS=sales@company.com")
        print("  3. Run this script again to verify")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    check_config()
