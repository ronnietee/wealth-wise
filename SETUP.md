# STEWARD Setup Guide

## Environment Variables Setup

### 1. Create Environment File
Copy the example environment file:
```bash
cp env.example .env
```

### 2. Configure Email Settings (for Password Reset)
Edit the `.env` file and update the email settings:

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@steward.com
```

### 3. Gmail Setup (if using Gmail)
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this password in `MAIL_PASSWORD` (not your regular Gmail password)

### 4. Other Email Providers
- **Outlook/Hotmail**: Use `smtp-mail.outlook.com` port 587
- **Yahoo**: Use `smtp.mail.yahoo.com` port 587
- **Custom SMTP**: Update `MAIL_SERVER` and `MAIL_PORT` accordingly

### 5. Database Setup
The app will automatically create the database tables on first run. No additional setup needed.

### 6. Run the Application
```bash
python app.py
```

## Troubleshooting

### Email Not Sending
1. Check your email credentials in `.env`
2. Ensure 2FA is enabled and app password is used (for Gmail)
3. Check firewall settings
4. Verify SMTP server and port settings

### Database Errors
1. Delete `instance/wealthwise.db` if you get relationship errors
2. Restart the application to recreate the database

### Login Issues
1. Check browser console for error messages
2. Verify the server is running without errors
3. Check network tab for API response status

## Features
- ✅ User registration and login
- ✅ Username or email login
- ✅ Forgot password with email reset
- ✅ Budget management
- ✅ Transaction tracking
- ✅ Category management
- ✅ Data export
- ✅ Settings management
