# SQLite to PostgreSQL Migration Guide

## Overview

This guide helps you migrate your Wealth Wise database from SQLite to PostgreSQL for production deployment.

## Method 1: Using Flask-Migrate (Recommended)

Since the application already uses Flask-Migrate and Alembic, the easiest approach is:

1. **Point Flask to PostgreSQL** (using environment variables or config)
2. **Run migrations** to create the schema in PostgreSQL
3. **Export/Import data** separately

```bash
# Set PostgreSQL database URL
export DATABASE_URL="postgresql://user:password@localhost/wealthwise"

# Initialize or upgrade database
flask db upgrade
```

## Method 2: Extract DDL and Convert Manually

### Step 1: Extract DDL from SQLite

```bash
python extract_ddl.py instance/wealthwise_dev.db > sqlite_ddl.sql
```

### Step 2: Key Conversions Needed

#### 1. Data Types

| SQLite | PostgreSQL | Notes |
|--------|------------|-------|
| `INTEGER` | `INTEGER` or `SERIAL` | Use SERIAL for auto-incrementing primary keys |
| `TEXT` | `TEXT` or `VARCHAR(n)` | Keep TEXT or specify VARCHAR |
| `REAL` | `DOUBLE PRECISION` or `NUMERIC` | For money, consider NUMERIC(10,2) |
| `BLOB` | `BYTEA` | Not used in this app |
| `BOOLEAN` | `BOOLEAN` | SQLite stores as INTEGER(0/1), PostgreSQL uses TRUE/FALSE |
| `DATE` | `DATE` | Compatible |
| `DATETIME` | `TIMESTAMP` or `TIMESTAMP WITH TIME ZONE` | Consider TIMESTAMPTZ for timezone awareness |

#### 2. Auto-Increment Primary Keys

**SQLite:**
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
```

**PostgreSQL:**
```sql
id SERIAL PRIMARY KEY
-- or in newer versions:
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY
```

#### 3. Default Values for Timestamps

**SQLite:**
```sql
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

**PostgreSQL:**
```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- or with timezone:
created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
```

#### 4. Boolean Defaults

**SQLite:**
```sql
is_active BOOLEAN DEFAULT 0
```

**PostgreSQL:**
```sql
is_active BOOLEAN DEFAULT FALSE
```

#### 5. Foreign Key Constraints

Both databases support foreign keys, but PostgreSQL enforces them more strictly. Ensure:

- Referenced tables exist
- Referenced columns have matching types
- Add `ON DELETE CASCADE` if needed (already in your models)

#### 6. Unique Constraints

**SQLite:**
```sql
UNIQUE (name, category_id)
```

**PostgreSQL:**
```sql
UNIQUE (name, category_id)
-- or with a name:
CONSTRAINT uq_subcategory_name_category UNIQUE (name, category_id)
```

#### 7. Quotes and Identifiers

- PostgreSQL is case-sensitive for quoted identifiers
- Unquoted identifiers are lowercased
- Use lowercase, unquoted table/column names for consistency

### Step 3: Example Conversion

**SQLite CREATE TABLE:**
```sql
CREATE TABLE "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "username" VARCHAR(80) NOT NULL UNIQUE,
    "email" VARCHAR(120) NOT NULL UNIQUE,
    "password_hash" VARCHAR(120) NOT NULL,
    "currency" VARCHAR(10) DEFAULT 'USD',
    "email_verified" BOOLEAN DEFAULT 0,
    "created_at" DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**PostgreSQL CREATE TABLE:**
```sql
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(120) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Method 3: Using SQLAlchemy Models (Best Practice)

Since you're using SQLAlchemy, the models are already database-agnostic. Simply:

1. **Change the database URI** in your config
2. **Run Flask-Migrate** to generate migrations for PostgreSQL
3. **Apply migrations** to create the schema

The models will automatically generate the correct DDL for PostgreSQL.

## Data Migration

After schema migration:

### Option A: SQLAlchemy Script

```python
# migrate_data.py
from src import create_app
from src.extensions import db
from src.models import *

app = create_app('production')

# Connect to SQLite
sqlite_uri = 'sqlite:///instance/wealthwise_dev.db'
# Connect to PostgreSQL
postgres_uri = 'postgresql://user:pass@localhost/wealthwise'

# Extract from SQLite, insert into PostgreSQL
# (Write script to copy data between databases)
```

### Option B: Using pgloader

```bash
pgloader sqlite:///instance/wealthwise_dev.db postgresql://user:pass@localhost/wealthwise
```

## Recommendations

1. **Use Flask-Migrate**: Since it's already set up, generate migrations for PostgreSQL
2. **Test First**: Create a staging PostgreSQL database to test the migration
3. **Backup**: Always backup both SQLite and PostgreSQL databases
4. **Incremental Migration**: Consider migrating in stages:
   - Schema first
   - Core data (users, categories)
   - Transactional data

## PostgreSQL-Specific Considerations

### Performance

- Add indexes on foreign keys and frequently queried columns
- Consider partitioning for large transaction tables
- Use `EXPLAIN ANALYZE` to optimize queries

### Data Integrity

- PostgreSQL's stricter type checking may catch issues SQLite missed
- Review foreign key constraints
- Check default value handling

### Features to Leverage

- **Full-text search** for transaction descriptions
- **Array types** if you need to store lists
- **JSON columns** for flexible metadata
- **Triggers** for audit logging
- **Materialized views** for reporting

## Checklist

- [ ] Extract SQLite DDL (optional)
- [ ] Set PostgreSQL connection string
- [ ] Generate Flask-Migrate migrations
- [ ] Review and adjust migrations if needed
- [ ] Test schema creation in staging
- [ ] Migrate data
- [ ] Verify data integrity
- [ ] Update application config
- [ ] Deploy and test
- [ ] Set up backups for PostgreSQL

