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

## 📚 Quick Links

- [Database Documentation](./database/README.md)
- [ERD (Entity Relationship Diagram)](./database/DATABASE_ERD.md)
- [SQLite vs PostgreSQL Guide](./database/SQLITE_VS_POSTGRESQL.md)
- [Migration Guide](./database/MIGRATION_GUIDE.md)
 - [Billing & Subscriptions](./billing/README.md)

