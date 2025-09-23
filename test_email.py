#!/usr/bin/env python3
"""
Test email configuration for STEWARD
Run this script to test if your email settings work
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email():
    """Test email configuration"""
    
    # Get email settings from environment
    mail_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.environ.get('MAIL_PORT', 587))
    mail_username = os.environ.get('MAIL_USERNAME')
    mail_password = os.environ.get('MAIL_PASSWORD')
    mail_sender = os.environ.get('MAIL_DEFAULT_SENDER', mail_username)
    
    if not mail_username or not mail_password:
        print("❌ Email configuration missing!")
        print("Please set MAIL_USERNAME and MAIL_PASSWORD in your .env file")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = mail_sender
        msg['To'] = mail_username  # Send to yourself for testing
        msg['Subject'] = "STEWARD Email Test"
        
        body = """
        <html>
        <body>
            <h2>STEWARD Email Test</h2>
            <p>If you receive this email, your STEWARD email configuration is working correctly!</p>
            <p>You can now use the forgot password functionality.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to server and send email
        print(f"🔗 Connecting to {mail_server}:{mail_port}...")
        server = smtplib.SMTP(mail_server, mail_port)
        
        if os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true':
            print("🔒 Starting TLS...")
            server.starttls()
        
        print(f"🔑 Logging in as {mail_username}...")
        server.login(mail_username, mail_password)
        
        print("📧 Sending test email...")
        server.sendmail(mail_sender, mail_username, msg.as_string())
        server.quit()
        
        print("✅ Email test successful!")
        print(f"📬 Check your inbox at {mail_username}")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your email credentials in .env file")
        print("2. For Gmail: Use App Password, not regular password")
        print("3. Ensure 2-Step Verification is enabled")
        print("4. Check firewall/antivirus settings")
        return False

if __name__ == "__main__":
    print("🧪 Testing STEWARD Email Configuration...")
    print("=" * 50)
    test_email()
