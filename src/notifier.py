"""
Notification system for email and Telegram alerts
"""
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from config.settings import (
    ENABLE_EMAIL_NOTIFICATIONS, EMAIL_HOST, EMAIL_PORT,
    EMAIL_USER, EMAIL_PASSWORD, NOTIFICATION_EMAIL,
    ENABLE_TELEGRAM_NOTIFICATIONS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
)
from src.logger import logger


class Notifier:
    def __init__(self):
        self.email_enabled = ENABLE_EMAIL_NOTIFICATIONS
        self.telegram_enabled = ENABLE_TELEGRAM_NOTIFICATIONS

    def send_email(self, subject: str, message: str) -> bool:
        """
        Send email notification

        Args:
            subject: Email subject
            message: Email message

        Returns:
            True if successful
        """
        if not self.email_enabled:
            return False

        if not all([EMAIL_USER, EMAIL_PASSWORD, NOTIFICATION_EMAIL]):
            logger.warning("Email credentials not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = NOTIFICATION_EMAIL
            msg['Subject'] = subject

            # Email body
            body = f"""
            AI Content Creator Notification

            {message}

            ---
            This is an automated notification from AI Content Creator.
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)

            logger.success(f"Email sent: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_telegram(self, message: str) -> bool:
        """
        Send Telegram notification

        Args:
            message: Message to send

        Returns:
            True if successful
        """
        if not self.telegram_enabled:
            return False

        if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
            logger.warning("Telegram credentials not configured")
            return False

        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': f"🤖 *AI Content Creator*\n\n{message}",
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, json=payload)

            if response.status_code == 200:
                logger.success("Telegram notification sent")
                return True
            else:
                logger.error(f"Failed to send Telegram: {response.json()}")
                return False

        except Exception as e:
            logger.error(f"Error sending Telegram: {str(e)}")
            return False

    def notify(self, title: str, message: str, level: str = 'info'):
        """
        Send notification via all enabled channels

        Args:
            title: Notification title
            message: Notification message
            level: Message level (info, success, warning, error)
        """
        # Add emoji based on level
        emoji_map = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }

        emoji = emoji_map.get(level, 'ℹ️')
        formatted_message = f"{emoji} {message}"

        # Send via email
        if self.email_enabled:
            self.send_email(f"{title}", formatted_message)

        # Send via Telegram
        if self.telegram_enabled:
            self.send_telegram(formatted_message)

    def notify_upload_success(self, clip_number: int, total_clips: int,
                             post_id: str):
        """Notify successful upload"""
        message = (
            f"Upload Successful!\n\n"
            f"Clip: {clip_number}/{total_clips}\n"
            f"Post ID: {post_id}"
        )
        self.notify("Upload Success", message, "success")

    def notify_upload_failure(self, clip_number: int, error: str):
        """Notify failed upload"""
        message = (
            f"Upload Failed!\n\n"
            f"Clip: {clip_number}\n"
            f"Error: {error}"
        )
        self.notify("Upload Failed", message, "error")

    def notify_video_complete(self, video_name: str, total_clips: int):
        """Notify when all clips uploaded"""
        message = (
            f"Video Complete! 🎉\n\n"
            f"Video: {video_name}\n"
            f"Total Clips: {total_clips}\n"
            f"All clips uploaded successfully!"
        )
        self.notify("Video Complete", message, "success")

    def notify_error(self, error_type: str, error_message: str):
        """Notify system error"""
        message = (
            f"System Error!\n\n"
            f"Type: {error_type}\n"
            f"Error: {error_message}"
        )
        self.notify("System Error", message, "error")

    def test_notifications(self):
        """Test all notification channels"""
        logger.info("Testing notification systems...")

        test_message = "This is a test notification from AI Content Creator"

        if self.email_enabled:
            success = self.send_email("Test Notification", test_message)
            if success:
                logger.success("Email test successful")
            else:
                logger.error("Email test failed")

        if self.telegram_enabled:
            success = self.send_telegram(test_message)
            if success:
                logger.success("Telegram test successful")
            else:
                logger.error("Telegram test failed")

        if not self.email_enabled and not self.telegram_enabled:
            logger.info("No notification channels enabled")
