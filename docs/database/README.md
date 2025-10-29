# Database Documentation

This directory contains all database-related documentation, migration guides, and optimization plans for the Wealth Wise application.

## 📚 Documentation Index

### Essential Reading

1. **[SQLITE_VS_POSTGRESQL.md](./SQLITE_VS_POSTGRESQL.md)** ⭐ **START HERE**
   - Should I use SQLite or PostgreSQL for deployment?
   - Decision guide for choosing the right database
   - When to migrate from SQLite to PostgreSQL

2. **[DATABASE_ERD.md](./DATABASE_ERD.md)**
   - Visual Entity Relationship Diagram
   - Complete database schema overview
   - Entity descriptions and relationships

### Migration Guides

3. **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)**
   - Step-by-step guide for migrating from SQLite to PostgreSQL
   - Data type conversions
   - Migration best practices

4. **[extract_ddl.py](./extract_ddl.py)**
   - Script to extract DDL from SQLite database
   - Usage: `python docs/database/extract_ddl.py instance/wealthwise_dev.db`

### Optimization (Future Reference)

5. **[FUTURE_OPTIMIZATION_NOTES.md](./FUTURE_OPTIMIZATION_NOTES.md)** ⭐ **Quick Reference**
   - When to optimize (10k+ users, production prep)
   - Quick checklist for future optimizations

6. **[DATABASE_OPTIMIZATION.md](./DATABASE_OPTIMIZATION.md)**
   - Complete optimization guide for 100k+ users
   - Indexing strategies
   - Performance tuning recommendations

7. **[OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)**
   - Summary of optimization recommendations
   - Quick answers to common questions

### Tools & Scripts

8. **[add_performance_indexes.py](./add_performance_indexes.py)**
   - Script to add performance indexes to PostgreSQL
   - Run after migrating to PostgreSQL
   - Usage: `python docs/database/add_performance_indexes.py`

9. **[add_optimization_migration.py](./add_optimization_migration.py)**
   - Flask-Migrate template for optimization migrations
   - Reference for creating migrations

## 🗺️ Quick Navigation

### I want to...

**...understand the database structure**
→ Read [DATABASE_ERD.md](./DATABASE_ERD.md)

**...decide on SQLite vs PostgreSQL**
→ Read [SQLITE_VS_POSTGRESQL.md](./SQLITE_VS_POSTGRESQL.md)

**...migrate from SQLite to PostgreSQL**
→ Read [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) and use [extract_ddl.py](./extract_ddl.py)

**...optimize for performance**
→ Read [FUTURE_OPTIMIZATION_NOTES.md](./FUTURE_OPTIMIZATION_NOTES.md) first, then [DATABASE_OPTIMIZATION.md](./DATABASE_OPTIMIZATION.md)

**...add indexes after migration**
→ Use [add_performance_indexes.py](./add_performance_indexes.py)

## 📋 Current Status

- **Current Database**: SQLite (development)
- **Production Database**: TBD (SQLite recommended initially)
- **Optimization Status**: Deferred (early development stage)

## 📝 Notes

- All optimization documentation is for **future reference**
- Current SQLite setup is perfect for development
- Revisit optimizations when you have 10k+ users or prepare for production
- All documentation assumes PostgreSQL for production-scale deployments

## 🔄 Documentation Updates

These documents were created during early development and should be reviewed:
- When preparing for production deployment
- When experiencing performance issues
- When scaling beyond 10,000 active users
- When migrating to PostgreSQL

