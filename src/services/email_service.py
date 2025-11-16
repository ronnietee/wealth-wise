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
        
        # Use CONTACT_EMAIL if set, otherwise fall back to MAIL_USERNAME (admin email)
        recipient_email = app_config.get('CONTACT_EMAIL') or app_config.get('MAIL_USERNAME')
        
        if not recipient_email:
            print("Error: No contact email configured. Set CONTACT_EMAIL or MAIL_USERNAME in .env")
            return False
        
        return send_email(
            to_email=recipient_email,
            subject=f"Contact Form: {subject}",
            body=body,
            app_config=app_config
        )
    
    @staticmethod
    def send_subscription_email(user, email_type, app_config, **kwargs):
        """Send subscription-related emails.
        
        Args:
            user: User model instance
            email_type: Type of email ('trial_started', 'trial_ending', 'payment_success', 
                       'payment_failed', 'subscription_activated', 'subscription_cancelled',
                       'subscription_expired', 'upgrade', 'downgrade')
            app_config: Flask app config
            **kwargs: Additional data for email content
        """
        from flask import request
        from ..utils.email import send_email
        
        templates = {
            'trial_started': {
                'subject': 'Welcome! Your Trial Has Started - STEWARD',
                'body': f"""
                <html>
                <body>
                    <h2>Welcome to STEWARD, {user.first_name}!</h2>
                    <p>Your {kwargs.get('trial_days', 30)}-day trial has started. Explore all our features risk-free.</p>
                    <p><strong>Trial Period:</strong> {kwargs.get('trial_start', 'N/A')} to {kwargs.get('trial_end', 'N/A')}</p>
                    <p><strong>Plan:</strong> {kwargs.get('plan', 'Monthly').capitalize()}</p>
                    <p>Enjoy full access during your trial. If you have any questions, feel free to contact us.</p>
                    <p>Best regards,<br>The STEWARD Team</p>
                </body>
                </html>
                """
            },
            'trial_ending': {
                'subject': 'Your Trial is Ending Soon - STEWARD',
                'body': f"""
                <html>
                <body>
                    <h2>Trial Ending Soon</h2>
                    <p>Hi {user.first_name},</p>
                    <p>Your trial period ends on {kwargs.get('trial_end', 'N/A')}. Subscribe now to continue enjoying STEWARD.</p>
                    <p><a href="{request.url_root}settings" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Manage Subscription</a></p>
                    <p>Best regards,<br>The STEWARD Team</p>
                </body>
                </html>
                """
            },
            'payment_success': {
                'subject': 'Payment Successful - STEWARD',
                'body': f"""
                <html>
                <body>
                    <h2>Payment Successful</h2>
                    <p>Hi {user.first_name},</p>
                    <p>Your payment of {kwargs.get('amount', 'N/A')} has been processed successfully.</p>
                    <p><strong>Payment Reference:</strong> {kwargs.get('reference', 'N/A')}</p>
                    <p>Thank you for your subscription!</p>
                    <p>Best regards,<br>The STEWARD Team</p>
                </body>
                </html>
                """
            },
            'payment_failed': {
                'subject': 'Payment Failed - STEWARD',
                'body': f"""
                <html>
                <body>
                    <h2>Payment Failed</h2>
                    <p>Hi {user.first_name},</p>
                    <p>We were unable to process your payment. Please update your payment method.</p>
                    <p><a href="{request.url_root}settings" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Update Payment</a></p>
                    <p>If you continue to experience issues, please contact support.</p>
                    <p>Best regards,<br>The STEWARD Team</p>
                </body>
                </html>
                """
            },
            'subscription_activated': {
                'subject': 'Subscription Activated - STEWARD',
                'body': f"""
                <html>
                <body>
                    <h2>Subscription Activated</h2>
                    <p>Hi {user.first_name},</p>
                    <p>Your subscription has been activated successfully!</p>
                    <p><strong>Plan:</strong> {kwargs.get('plan', 'N/A').capitalize()}</p>
                    <p><strong>Next Billing Date:</strong> {kwargs.get('next_billing', 'N/A')}</p>
                    <p>Thank you for subscribing to STEWARD!</p>
                    <p>Best regards,<br>The STEWARD Team</p>
                </body>
                </html>
                """
            },
            'subscription_cancelled': {
                'subject': 'Subscription Cancelled - STEWARD',
                'body': f"""
                <html>
                <body>
                    <h2>Subscription Cancelled</h2>
                    <p>Hi {user.first_name},</p>
                    <p>Your subscription has been cancelled.</p>
                    <p>{'You will retain access until ' + kwargs.get('cancel_at', 'N/A') if kwargs.get('cancel_at') else 'Access has been revoked immediately.'}</p>
                    <p>We're sorry to see you go. If you change your mind, you can resubscribe anytime.</p>
                    <p>Best regards,<br>The STEWARD Team</p>
                </body>
                </html>
                """
            },
            'upgrade': {
                'subject': 'Subscription Upgraded - STEWARD',
                'body': f"""
                <html>
                <body>
                    <h2>Subscription Upgraded</h2>
                    <p>Hi {user.first_name},</p>
                    <p>Your subscription has been upgraded to {kwargs.get('new_plan', 'N/A').capitalize()}.</p>
                    <p>Enjoy your enhanced features!</p>
                    <p>Best regards,<br>The STEWARD Team</p>
                </body>
                </html>
                """
            },
            'downgrade': {
                'subject': 'Subscription Changed - STEWARD',
                'body': f"""
                <html>
                <body>
                    <h2>Subscription Changed</h2>
                    <p>Hi {user.first_name},</p>
                    <p>Your subscription has been changed to {kwargs.get('new_plan', 'N/A').capitalize()}.</p>
                    <p>The change will take effect at your next billing cycle.</p>
                    <p>Best regards,<br>The STEWARD Team</p>
                </body>
                </html>
                """
            }
        }
        
        if email_type not in templates:
            return False
        
        template = templates[email_type]
        return send_email(
            to_email=user.email,
            subject=template['subject'],
            body=template['body'],
            app_config=app_config
        )