"""
Email utility functions.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import request


def send_email(to_email, subject, body, app_config):
    """Send email using SendGrid (preferred) or SMTP (fallback)."""
    from flask import current_app
    import os
    
    # Try SendGrid first (works with Render and other platforms)
    sendgrid_api_key = app_config.get('SENDGRID_API_KEY')
    if sendgrid_api_key:
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            from_email = app_config.get('SENDGRID_FROM_EMAIL') or app_config.get('MAIL_DEFAULT_SENDER', 'noreply@steward.com')
            
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=body
            )
            
            sg = SendGridAPIClient(sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                if os.environ.get('FLASK_ENV') == 'development':
                    print(f"Email sent successfully via SendGrid to {to_email}")
                else:
                    current_app.logger.info(f"Email sent successfully via SendGrid to {to_email}")
                return True
            else:
                error_msg = f"SendGrid API error: Status {response.status_code}"
                if os.environ.get('FLASK_ENV') == 'production':
                    current_app.logger.error(error_msg)
                else:
                    print(error_msg)
                # Fall through to SMTP if SendGrid fails
        except ImportError:
            error_msg = "SendGrid package not installed. Install with: pip install sendgrid"
            if os.environ.get('FLASK_ENV') == 'production':
                current_app.logger.error(error_msg)
            else:
                print(error_msg)
            # Fall through to SMTP
        except Exception as e:
            error_msg = f"SendGrid error: {type(e).__name__}: {str(e)}"
            if os.environ.get('FLASK_ENV') == 'production':
                current_app.logger.warning(error_msg + " - Falling back to SMTP")
            else:
                print(error_msg + " - Falling back to SMTP")
            # Fall through to SMTP
    
    # Fallback to SMTP if SendGrid is not configured or failed
    try:
        # Validate SMTP email configuration
        if not app_config.get('MAIL_SERVER'):
            error_msg = "Error: Neither SendGrid nor SMTP configured"
            if os.environ.get('FLASK_ENV') == 'production':
                current_app.logger.error(error_msg)
            else:
                print(error_msg)
            return False
        
        if not app_config.get('MAIL_USERNAME') or not app_config.get('MAIL_PASSWORD'):
            error_msg = "Error: MAIL_USERNAME or MAIL_PASSWORD not configured"
            if os.environ.get('FLASK_ENV') == 'production':
                current_app.logger.error(error_msg)
            else:
                print(error_msg)
            return False
        
        msg = MIMEMultipart()
        msg['From'] = app_config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        mail_server = app_config['MAIL_SERVER']
        mail_port = app_config.get('MAIL_PORT', 587)
        use_tls = app_config.get('MAIL_USE_TLS', True)
        use_ssl = app_config.get('MAIL_USE_SSL', False)
        
        # Use SMTP_SSL for SSL connections (port 465), regular SMTP for TLS (port 587)
        # Add timeout to prevent hanging (10 seconds for connection, 30 seconds for operations)
        if use_ssl:
            server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=10)
        else:
            server = smtplib.SMTP(mail_server, mail_port, timeout=10)
            if use_tls:
                server.starttls()
        
        # Set timeout for all operations (30 seconds total)
        import socket
        if hasattr(server, 'sock') and server.sock:
            server.sock.settimeout(30)
        
        # Only enable debug in development
        if os.environ.get('FLASK_ENV') == 'development':
            server.set_debuglevel(1)
            print(f"Attempting to connect to SMTP server: {mail_server}:{mail_port}, TLS: {use_tls}, SSL: {use_ssl}")
        else:
            current_app.logger.info(f"Connecting to SMTP server: {mail_server}:{mail_port}, TLS: {use_tls}, SSL: {use_ssl}")
        
        username = app_config['MAIL_USERNAME']
        password = app_config['MAIL_PASSWORD']
        
        if os.environ.get('FLASK_ENV') == 'development':
            print(f"Attempting to login with username: {username}")
        else:
            current_app.logger.info(f"Logging in to SMTP server with username: {username}")
        
        server.login(username, password)
        
        text = msg.as_string()
        server.sendmail(app_config['MAIL_DEFAULT_SENDER'], to_email, text)
        server.quit()
        
        if os.environ.get('FLASK_ENV') == 'development':
            print(f"Email sent successfully to {to_email}")
        else:
            current_app.logger.info(f"Email sent successfully to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication Error: {str(e)}"
        if os.environ.get('FLASK_ENV') == 'production':
            current_app.logger.error(error_msg, exc_info=True)
        else:
            print(error_msg)
        return False
    except smtplib.SMTPException as e:
        error_msg = f"SMTP Error: {str(e)}"
        if os.environ.get('FLASK_ENV') == 'production':
            current_app.logger.error(error_msg, exc_info=True)
        else:
            print(error_msg)
        return False
    except Exception as e:
        error_msg = f"Error sending email: {type(e).__name__}: {str(e)}"
        if os.environ.get('FLASK_ENV') == 'production':
            current_app.logger.error(error_msg, exc_info=True)
        else:
            print(error_msg)
            import traceback
            traceback.print_exc()
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
