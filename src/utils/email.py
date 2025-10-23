"""
Email utility functions.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import request


def send_email(to_email, subject, body, app_config):
    """Send email using SMTP."""
    try:
        msg = MIMEMultipart()
        msg['From'] = app_config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(app_config['MAIL_SERVER'], app_config['MAIL_PORT'])
        if app_config['MAIL_USE_TLS']:
            server.starttls()
        
        if app_config['MAIL_USERNAME'] and app_config['MAIL_PASSWORD']:
            server.login(app_config['MAIL_USERNAME'], app_config['MAIL_PASSWORD'])
        
        text = msg.as_string()
        server.sendmail(app_config['MAIL_DEFAULT_SENDER'], to_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_verification_email(user, verification_token, app_config):
    """Send email verification email."""
    verification_url = f"{request.url_root}verify-email?token={verification_token}"
    
    subject = "Verify Your Email - STEWARD"
    body = f"""
    <html>
    <body>
        <h2>Welcome to STEWARD!</h2>
        <p>Hi {user.first_name},</p>
        <p>Thank you for registering with STEWARD. Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p>{verification_url}</p>
        <p>This link will expire in 24 hours.</p>
        <p>Best regards,<br>The STEWARD Team</p>
    </body>
    </html>
    """
    
    return send_email(user.email, subject, body, app_config)


def send_password_reset_email(user, reset_token, app_config):
    """Send password reset email."""
    reset_url = f"{request.url_root}reset-password?token={reset_token}"
    
    subject = "Reset Your Password - STEWARD"
    body = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>Hi {user.first_name},</p>
        <p>You requested to reset your password for your STEWARD account.</p>
        <p>Click the link below to reset your password:</p>
        <p><a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p>{reset_url}</p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this password reset, please ignore this email.</p>
        <p>Best regards,<br>The STEWARD Team</p>
    </body>
    </html>
    """
    
    return send_email(user.email, subject, body, app_config)
