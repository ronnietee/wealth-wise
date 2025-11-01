# Admin Portal Setup Guide

## Quick Setup

The admin portal uses **separate credentials** stored in environment variables. No user account registration is needed!

### 1. Configure Admin Credentials

Add these to your `.env` file:

```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password-here
```

**Security Best Practices:**
- Use a strong, unique password (minimum 16 characters recommended)
- Never commit `.env` file to version control
- Change default username in production
- Consider using a password manager to generate secure passwords

### 2. Access Admin Portal

1. Navigate to: `http://localhost:5000/admin`
2. Enter your admin credentials:
   - **Username**: The value of `ADMIN_USERNAME` from your `.env`
   - **Password**: The value of `ADMIN_PASSWORD` from your `.env`
3. Click "Login"

### 3. Features Available

Once logged in, you can:
- View subscription statistics and manage subscriptions
- View payment history and statistics
- Process subscription renewals manually
- Toggle payment enforcement settings
- Access all admin API endpoints

## Authentication Methods

The admin portal supports two authentication methods:

### 1. Session-Based (Web Portal)
- Uses Flask sessions
- Automatically expires after 24 hours
- Used by the web interface at `/admin/*`

### 2. Token-Based (API Access)
- JWT tokens with `admin: true` claim
- Valid for 24 hours
- Used for API endpoints and cron jobs
- Get token from `/admin/login` endpoint

## API Access

For API access or cron jobs, you can authenticate using the admin token:

```bash
# Get admin token
curl -X POST http://localhost:5000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Use token for API calls
curl -X GET http://localhost:5000/api/subscriptions/admin/subscriptions \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Troubleshooting

### "Admin access not configured"
- Make sure `ADMIN_PASSWORD` is set in your `.env` file
- Restart the Flask application after adding credentials

### "Invalid credentials"
- Verify `ADMIN_USERNAME` and `ADMIN_PASSWORD` match what's in `.env`
- Check for extra spaces or special characters
- Ensure `.env` file is loaded (check Flask startup logs)

### Session Expired
- Admin sessions expire after 24 hours
- Simply log in again to create a new session

## Security Recommendations

1. **Change Default Credentials**: Never use default `admin`/`admin` in production
2. **Use Environment Variables**: Store credentials in `.env`, never in code
3. **Strong Passwords**: Use a password manager to generate secure passwords
4. **HTTPS in Production**: Always use HTTPS for admin portal in production
5. **IP Restrictions**: Consider adding IP whitelisting for admin routes in production
6. **Monitor Access**: Review server logs regularly for admin access attempts

## Environment Variables Reference

```bash
# Required for admin access
ADMIN_USERNAME=admin              # Admin username (default: 'admin')
ADMIN_PASSWORD=your-password      # Admin password (REQUIRED - no default)
```

## Backward Compatibility

The system supports both credential-based and user-based admin access:

- **Credential-based** (Primary): Uses `ADMIN_USERNAME`/`ADMIN_PASSWORD` from environment
  - Used by web portal (`/admin/*`)
  - Creates admin JWT tokens for API access
  
- **User-based** (Optional): Uses `is_admin` flag on User model
  - Still supported for API token authentication
  - Useful if you want to promote regular users to admin
  - Not used by web portal (web portal only uses credentials)

You can use both systems simultaneously if needed.

