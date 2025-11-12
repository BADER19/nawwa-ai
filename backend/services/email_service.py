import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from datetime import datetime, timedelta
import secrets
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("email_service")

# Email configuration from environment
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@nawwa.ai")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
APP_NAME = "Nawwa AI"

# Thread pool for sending emails asynchronously
executor = ThreadPoolExecutor(max_workers=2)


def generate_token() -> str:
    """Generate a secure random token for verification or password reset"""
    return secrets.token_urlsafe(32)


def send_email_sync(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
    """Synchronously send an email"""
    try:
        if not EMAIL_USERNAME or not EMAIL_PASSWORD:
            logger.warning("Email credentials not configured. Skipping email send.")
            logger.info(f"Would have sent email to {to_email}: {subject}")
            return False

        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email
        msg["Subject"] = subject

        # Add text and HTML parts
        if text_body:
            part1 = MIMEText(text_body, "plain")
            msg.attach(part1)

        part2 = MIMEText(html_body, "html")
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            if EMAIL_USE_TLS:
                server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def send_email_async(to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
    """Asynchronously send an email using thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        send_email_sync,
        to_email,
        subject,
        html_body,
        text_body
    )


def send_verification_email(to_email: str, username: str, verification_token: str) -> bool:
    """Send email verification link"""
    verification_url = f"{FRONTEND_URL}/verify-email?token={verification_token}"

    subject = f"Verify your {APP_NAME} account"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 14px 28px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #6b7280; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{APP_NAME}</h1>
                <p>Welcome to the future of visual AI</p>
            </div>
            <div class="content">
                <h2>Hi {username},</h2>
                <p>Thanks for signing up! Please verify your email address by clicking the button below:</p>
                <a href="{verification_url}" class="button">Verify Email Address</a>
                <p style="margin-top: 20px;">Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_url}</p>
                <p class="footer">This link will expire in 24 hours. If you didn't create an account with {APP_NAME}, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Hi {username},

    Thanks for signing up for {APP_NAME}!

    Please verify your email address by clicking this link:
    {verification_url}

    This link will expire in 24 hours.

    If you didn't create an account with {APP_NAME}, please ignore this email.

    Best regards,
    The {APP_NAME} Team
    """

    return send_email_sync(to_email, subject, html_body, text_body)


def send_password_reset_email(to_email: str, username: str, reset_token: str) -> bool:
    """Send password reset email"""
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"

    subject = f"Reset your {APP_NAME} password"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 14px 28px; background: #f5576c; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #6b7280; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{APP_NAME}</h1>
                <p>Password Reset Request</p>
            </div>
            <div class="content">
                <h2>Hi {username},</h2>
                <p>You requested to reset your password. Click the button below to create a new password:</p>
                <a href="{reset_url}" class="button">Reset Password</a>
                <p style="margin-top: 20px;">Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #f5576c;">{reset_url}</p>
                <p class="footer">This link will expire in 1 hour. If you didn't request this reset, please ignore this email and your password will remain unchanged.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Hi {username},

    You requested to reset your password for {APP_NAME}.

    Please click this link to create a new password:
    {reset_url}

    This link will expire in 1 hour.

    If you didn't request this reset, please ignore this email and your password will remain unchanged.

    Best regards,
    The {APP_NAME} Team
    """

    return send_email_sync(to_email, subject, html_body, text_body)


def send_2fa_code_email(to_email: str, username: str, code: str) -> bool:
    """Send 2FA verification code"""
    subject = f"{APP_NAME} - Your verification code"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .code {{ font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #4facfe; padding: 20px; background: white; border-radius: 5px; margin: 20px 0; text-align: center; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #6b7280; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{APP_NAME}</h1>
                <p>Two-Factor Authentication</p>
            </div>
            <div class="content">
                <h2>Hi {username},</h2>
                <p>Your verification code is:</p>
                <div class="code">{code}</div>
                <p>Enter this code to complete your login. The code will expire in 10 minutes.</p>
                <p class="footer">If you didn't request this code, please ignore this email and consider changing your password.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Hi {username},

    Your {APP_NAME} verification code is: {code}

    Enter this code to complete your login. The code will expire in 10 minutes.

    If you didn't request this code, please ignore this email and consider changing your password.

    Best regards,
    The {APP_NAME} Team
    """

    return send_email_sync(to_email, subject, html_body, text_body)


def send_welcome_email(to_email: str, username: str) -> bool:
    """Send welcome email after successful verification"""
    subject = f"Welcome to {APP_NAME}!"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 14px 28px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #6b7280; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to {APP_NAME}!</h1>
                <p>Your account is now verified</p>
            </div>
            <div class="content">
                <h2>Hi {username},</h2>
                <p>Your email has been verified successfully! You can now access all features of {APP_NAME}.</p>
                <p>Here are some things you can do:</p>
                <ul>
                    <li>Create instant visualizations with voice or text</li>
                    <li>Generate math plots and diagrams</li>
                    <li>Explore anatomy and geography visuals</li>
                    <li>Save and manage your workspaces</li>
                </ul>
                <a href="{FRONTEND_URL}/app" class="button">Start Creating</a>
                <p class="footer">Need help? Visit our docs or contact support at support@nawwa.ai</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Hi {username},

    Welcome to {APP_NAME}!

    Your email has been verified successfully. You can now access all features.

    Start creating: {FRONTEND_URL}/app

    Best regards,
    The {APP_NAME} Team
    """

    return send_email_sync(to_email, subject, html_body, text_body)