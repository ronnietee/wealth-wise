# STEWARD Documentation

Welcome to the STEWARD documentation. This directory contains comprehensive documentation for the application.

## 📚 Documentation Index

### Getting Started
- **[Main README](../README.md)** - Project overview, installation, and quick start guide

### Security & Privacy
- **[Security Implementation](SECURITY.md)** - Complete security implementation guide
  - Security features and configurations
  - Authentication and authorization
  - CSRF protection, rate limiting, security headers
  - Password requirements and validation
  - Security logging and monitoring

### Input Validation
- **[Input Validation Guide](VALIDATION.md)** - Marshmallow schema implementation
  - Schema overview and usage
  - Validation rules and error handling
  - XSS prevention and sanitization

### Database
- **[Database Documentation](database/README.md)** - Database structure and management
  - Entity Relationship Diagram (ERD)
  - Database optimization guide
  - Migration guide
  - SQLite vs PostgreSQL comparison

### Billing & Payments
- **[Billing Documentation](billing/README.md)** - Payment system documentation
  - Payment security
  - Admin setup
  - Onboarding flow
  - Cron job setup

### Legal
- **[Terms and Conditions](legal/TERMS_AND_CONDITIONS.md)** - Terms of service
- **[Privacy Policy](legal/PRIVACY_POLICY.md)** - Privacy policy

## 🗂️ Documentation Structure

```
docs/
├── README.md (this file)
├── SECURITY.md (consolidated security documentation)
├── VALIDATION.md (input validation documentation)
├── database/
│   ├── README.md
│   ├── DATABASE_ERD.md
│   ├── DATABASE_OPTIMIZATION.md
│   ├── MIGRATION_GUIDE.md
│   └── ...
├── billing/
│   ├── README.md
│   ├── PAYMENT_SECURITY.md
│   ├── ADMIN_SETUP.md
│   └── ...
└── legal/
    ├── TERMS_AND_CONDITIONS.md
    └── PRIVACY_POLICY.md
```

## 🔍 Quick Reference

### For Developers
- **Security**: See [SECURITY.md](SECURITY.md)
- **Validation**: See [VALIDATION.md](VALIDATION.md)
- **Database**: See [database/README.md](database/README.md)

### For Administrators
- **Admin Setup**: See [billing/ADMIN_SETUP.md](billing/ADMIN_SETUP.md)
- **Payment Security**: See [billing/PAYMENT_SECURITY.md](billing/PAYMENT_SECURITY.md)
- **Admin Password Setup**: 
  1. Run `python generate_admin_password.py` from the project root
  2. Enter your desired admin password
  3. Copy the generated hash to your `.env` file as `ADMIN_PASSWORD_HASH`
  4. Set `ADMIN_USERNAME=admin` (or your preferred username)

### For Users
- **Terms**: See [legal/TERMS_AND_CONDITIONS.md](legal/TERMS_AND_CONDITIONS.md)
- **Privacy**: See [legal/PRIVACY_POLICY.md](legal/PRIVACY_POLICY.md)

## 📝 Contributing to Documentation

When updating documentation:
1. Keep documentation in the appropriate subdirectory
2. Update this README if adding new sections
3. Ensure all links are working
4. Keep documentation concise and up-to-date
