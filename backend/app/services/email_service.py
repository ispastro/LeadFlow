import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_user = None
        self.smtp_password = None
        self.from_email = None
        self.notification_recipients = []
        self.enabled = False
    
    def configure(self, settings):
        """Configure email service from settings object"""
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email or settings.smtp_user
        self.notification_recipients = settings.notification_emails.split(",") if settings.notification_emails else []
        self.enabled = bool(self.smtp_user and self.smtp_password and self.notification_recipients and self.notification_recipients[0])
        self.dashboard_url = settings.dashboard_url

    def send_lead_notification(
        self,
        lead_email: str,
        lead_name: Optional[str],
        intent: Optional[str],
        quality: Optional[str],
        conversation_id: int,
        lead_id: int
    ):
        """Send email notification when new lead is captured"""
        if not self.enabled:
            logger.warning("Email service not configured - skipping notification")
            return

        try:
            subject = f"🎯 New Lead Captured: {lead_name or lead_email}"
            html_body = self._build_email_template(
                lead_email, lead_name, intent, quality, conversation_id, lead_id
            )

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.notification_recipients)
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Lead notification sent for lead_id={lead_id}")

        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")

    def _build_email_template(
        self,
        lead_email: str,
        lead_name: Optional[str],
        intent: Optional[str],
        quality: Optional[str],
        conversation_id: int,
        lead_id: int
    ) -> str:
        """Build HTML email template"""
        quality_emoji = {"hot": "🔥", "warm": "⚡", "cold": "❄️"}.get(quality, "📊")
        quality_color = {"hot": "#ef4444", "warm": "#f59e0b", "cold": "#3b82f6"}.get(quality, "#6b7280")
        
        conversation_url = f"{self.dashboard_url}/conversations?id={conversation_id}"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background-color: #f3f4f6;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%); padding: 30px; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 600;">
                                🎯 New Lead Captured!
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Lead Quality Badge -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px;">
                            <div style="display: inline-block; background-color: {quality_color}; color: #ffffff; padding: 8px 16px; border-radius: 6px; font-weight: 600; font-size: 14px;">
                                {quality_emoji} {quality.upper() if quality else 'NEW'} LEAD
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Lead Details -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                                        <strong style="color: #6b7280; font-size: 14px;">Name:</strong><br>
                                        <span style="color: #111827; font-size: 16px; font-weight: 500;">{lead_name or 'Not provided'}</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                                        <strong style="color: #6b7280; font-size: 14px;">Email:</strong><br>
                                        <a href="mailto:{lead_email}" style="color: #2563eb; font-size: 16px; text-decoration: none;">{lead_email}</a>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0; border-bottom: 1px solid #e5e7eb;">
                                        <strong style="color: #6b7280; font-size: 14px;">Intent:</strong><br>
                                        <span style="color: #111827; font-size: 16px;">{intent or 'General inquiry'}</span>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0;">
                                        <strong style="color: #6b7280; font-size: 14px;">Captured:</strong><br>
                                        <span style="color: #111827; font-size: 16px;">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- CTA Button -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <a href="{conversation_url}" style="display: inline-block; background-color: #000000; color: #ffffff; padding: 14px 28px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 16px;">
                                View Full Conversation →
                            </a>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 30px; background-color: #f9fafb; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0; color: #6b7280; font-size: 14px;">
                                💡 <strong>Pro Tip:</strong> Respond within 5 minutes to increase conversion by 21x
                            </p>
                        </td>
                    </tr>
                </table>
                
                <!-- Email Footer -->
                <table width="600" cellpadding="0" cellspacing="0" style="margin-top: 20px;">
                    <tr>
                        <td style="text-align: center; color: #9ca3af; font-size: 12px;">
                            <p style="margin: 0;">Sent by LeadFlow AI Sales Agent</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


email_service = EmailService()
