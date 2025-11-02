# Documentation

This directory contains all documentation for the Wealth Wise application.

## 📁 Directory Structure

```
docs/
├── database/           # Database documentation, migrations, and optimizations
├── billing/            # Subscriptions, PayFast integration, and billing guides
└── README.md           # This file
```

## 🗂️ Available Documentation

### Database Documentation

See [database/README.md](./database/README.md) for complete database documentation including:
- Entity Relationship Diagrams
- Migration guides (SQLite → PostgreSQL)
- Optimization plans (for future scaling)
- Deployment decision guides

### Billing & Subscriptions

See [billing/README.md](./billing/README.md) for comprehensive documentation covering:
- Environment variables and configuration
- Trial rules, subscription states, and enforcement toggles
- API endpoints for subscriptions (start, status, webhook, toggle)
- PayFast setup, signature validation, and payloads
- Test scenarios and manual verification steps

Additional billing documentation:
- [Payment Security](./billing/PAYMENT_SECURITY.md) - PCI compliance and payment security implementation
- [Onboarding Flow](./billing/ONBOARDING_FLOW.md) - Complete onboarding process documentation
- [Admin Setup](./billing/ADMIN_SETUP.md) - Admin portal configuration
- [Cron Setup](./billing/CRON_SETUP.md) - Automated renewal processing

## 📚 Quick Links

### Database
- [Database Documentation](./database/README.md)
- [ERD (Entity Relationship Diagram)](./database/DATABASE_ERD.md)
- [SQLite vs PostgreSQL Guide](./database/SQLITE_VS_POSTGRESQL.md)
- [Migration Guide](./database/MIGRATION_GUIDE.md)

### Billing & Subscriptions
- [Billing & Subscriptions Overview](./billing/README.md)
- [Payment Security](./billing/PAYMENT_SECURITY.md)
- [Onboarding Flow](./billing/ONBOARDING_FLOW.md)
- [Admin Setup](./billing/ADMIN_SETUP.md)
- [Cron Setup](./billing/CRON_SETUP.md)

