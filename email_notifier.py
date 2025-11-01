#!/usr/bin/env python3
"""
Email Notification System for Conference Deadline Changes
===========================================================

Sends email alerts when:
- New conferences are discovered
- Deadlines are changed/updated
- Deadlines are approaching (optional)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict
import os


class EmailNotifier:
    """Send email notifications for conference deadline changes."""

    def __init__(self, smtp_server='smtp.gmail.com', smtp_port=587):
        """
        Initialize email notifier.

        For Gmail:
        - smtp_server: 'smtp.gmail.com'
        - smtp_port: 587
        - Use App Password (not regular password)

        Environment variables needed:
        - EMAIL_FROM: Sender email address
        - EMAIL_PASSWORD: Email password or app password
        - EMAIL_TO: Recipient email address (can be same as FROM)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_to = os.getenv('EMAIL_TO', self.email_from)

    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return all([self.email_from, self.email_password, self.email_to])

    def send_notification(self, subject: str, body_html: str, body_text: str = None):
        """
        Send an email notification.

        Args:
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text alternative (optional)
        """
        if not self.is_configured():
            print("  ⚠️  Email not configured. Skipping notification.")
            print("     Set EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO environment variables")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject

            # Add plain text and HTML parts
            if body_text:
                part1 = MIMEText(body_text, 'plain')
                msg.attach(part1)

            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)

            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)

            print(f"  ✓ Email sent: {subject}")
            return True

        except Exception as e:
            print(f"  ❌ Email error: {str(e)[:100]}")
            return False

    def notify_changes(self, changes: List[tuple]):
        """
        Send notification about conference deadline changes.

        Args:
            changes: List of (conference_key, changes_dict) tuples
        """
        if not changes:
            return

        # Build email content
        subject = f"🔔 Conference Deadlines Update - {len(changes)} changes detected"

        # HTML body
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #333; }}
                .change {{ margin: 20px 0; padding: 15px; border-left: 4px solid #4CAF50; background-color: #f9f9f9; }}
                .new {{ border-left-color: #2196F3; }}
                .updated {{ border-left-color: #FF9800; }}
                .conf-name {{ font-weight: bold; font-size: 1.1em; color: #333; }}
                .deadline {{ color: #d32f2f; font-weight: bold; }}
                .old-deadline {{ text-decoration: line-through; color: #999; }}
                .arrow {{ color: #666; margin: 0 10px; }}
                .footer {{ margin-top: 30px; font-size: 0.9em; color: #666; }}
            </style>
        </head>
        <body>
            <h2>Conference Deadline Changes</h2>
            <p>Detected {len(changes)} change(s) on {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}</p>
        """

        text_body = f"Conference Deadline Changes\n{'=' * 50}\n\n"

        for conf_key, change_dict in changes:
            conf_name = conf_key.replace('_', ' ')

            if change_dict['is_new']:
                html += f"""
                <div class="change new">
                    <div class="conf-name">🆕 NEW: {conf_name}</div>
                    <div>Deadline: <span class="deadline">{change_dict.get('new_deadline', 'TBD')}</span></div>
                </div>
                """
                text_body += f"🆕 NEW: {conf_name}\n"
                text_body += f"   Deadline: {change_dict.get('new_deadline', 'TBD')}\n\n"

            elif change_dict['deadline_changed']:
                old_dl = change_dict.get('old_deadline', 'Unknown')
                new_dl = change_dict.get('new_deadline', 'Unknown')

                html += f"""
                <div class="change updated">
                    <div class="conf-name">🔄 UPDATED: {conf_name}</div>
                    <div>
                        Deadline changed:
                        <span class="old-deadline">{old_dl}</span>
                        <span class="arrow">→</span>
                        <span class="deadline">{new_dl}</span>
                    </div>
                </div>
                """
                text_body += f"🔄 UPDATED: {conf_name}\n"
                text_body += f"   {old_dl} → {new_dl}\n\n"

            elif change_dict['url_changed']:
                html += f"""
                <div class="change updated">
                    <div class="conf-name">🔗 URL CHANGED: {conf_name}</div>
                    <div>New URL: {change_dict.get('new_url', 'Unknown')}</div>
                </div>
                """
                text_body += f"🔗 URL CHANGED: {conf_name}\n"
                text_body += f"   New URL: {change_dict.get('new_url', 'Unknown')}\n\n"

        html += """
            <div class="footer">
                <p>This is an automated notification from your Conference Deadline Tracker.</p>
                <p>Check your Google Calendar for updated deadlines.</p>
            </div>
        </body>
        </html>
        """

        # Send email
        self.send_notification(subject, html, text_body)

    def test_email(self):
        """Send a test email to verify configuration."""
        if not self.is_configured():
            print("❌ Email not configured!")
            print("\nTo configure email notifications:")
            print("1. For Gmail users:")
            print("   - Enable 2-Step Verification")
            print("   - Generate an App Password: https://myaccount.google.com/apppasswords")
            print("   - Use the App Password, not your regular password")
            print("\n2. Set environment variables:")
            print("   export EMAIL_FROM='your.email@gmail.com'")
            print("   export EMAIL_PASSWORD='your-app-password'")
            print("   export EMAIL_TO='recipient@email.com'  # Optional, defaults to EMAIL_FROM")
            return False

        subject = "✅ Test Email - Conference Tracker"
        html = """
        <html>
        <body>
            <h2>Email Configuration Successful!</h2>
            <p>Your conference deadline tracker is configured to send notifications.</p>
            <p>You will receive emails when:</p>
            <ul>
                <li>New conferences are discovered</li>
                <li>Deadlines are changed</li>
                <li>URLs are updated</li>
            </ul>
            <p><em>This was a test message.</em></p>
        </body>
        </html>
        """
        text = "Email configuration successful! You will receive notifications for conference deadline changes."

        return self.send_notification(subject, html, text)


if __name__ == '__main__':
    # Test email configuration
    notifier = EmailNotifier()

    print("=" * 70)
    print("Email Notification System - Configuration Test")
    print("=" * 70)

    notifier.test_email()

    # Example: send change notification
    if notifier.is_configured():
        example_changes = [
            ('ISCA_2026', {
                'is_new': True,
                'new_deadline': 'November 10, 2025',
                'deadline_changed': False,
                'url_changed': False
            }),
            ('DAC_2026', {
                'is_new': False,
                'deadline_changed': True,
                'old_deadline': 'November 15, 2025',
                'new_deadline': 'November 22, 2025',
                'url_changed': False
            })
        ]

        print("\nSending example change notification...")
        notifier.notify_changes(example_changes)
