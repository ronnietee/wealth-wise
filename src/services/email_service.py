"""
Email service for sending various types of emails.
"""

from ..utils.email import send_verification_email, send_password_reset_email, send_email


class EmailService:
    """Service for handling email operations."""
    
    @staticmethod
    def send_verification_email(user, verification_token, app_config):
        """Send email verification email."""
        return send_verification_email(user, verification_token, app_config)
    
    @staticmethod
    def send_password_reset_email(user, reset_token, app_config):
        """Send password reset email."""
        return send_password_reset_email(user, reset_token, app_config)
    
    @staticmethod
    def send_contact_email(name, email, subject, message, app_config):
        """Send contact form email."""
        body = f"""
        <html>
        <body>
            <h2>New Contact Form Submission</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Message:</strong></p>
            <p>{message}</p>
        </body>
        </html>
        """
        
        return send_email(
            to_email=app_config['MAIL_DEFAULT_SENDER'],
            subject=f"Contact Form: {subject}",
            body=body,
            app_config=app_config
        )
