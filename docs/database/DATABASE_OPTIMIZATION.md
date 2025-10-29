# Database Optimization Plan for 100,000+ Users

> **NOTE**: This document is for **future reference** when you reach significant scale. Current SQLite setup is perfectly fine for development and early-stage growth. Refer to `FUTURE_OPTIMIZATION_NOTES.md` for when to revisit these optimizations.

## Executive Summary

This document outlines database optimizations for handling 100,000+ users with optimal performance. The strategy focuses on **indexing** (most critical), selective use of UUIDs, and strategic partitioning for high-growth tables.

**When to use this guide**: When you have 10,000+ active users, are preparing for production launch, or experiencing performance issues.

## 1. Indexing Strategy (CRITICAL - Do This First)

Indexing provides the biggest performance gains and should be implemented before any other optimization.

### 1.1 Foreign Key Indexes (Missing in SQLite)

PostgreSQL doesn't automatically index foreign keys. Add indexes on all FK columns:

```sql
-- Foreign key indexes (critical for joins and cascade operations)
CREATE INDEX idx_transaction_user_id ON transaction(user_id);
CREATE INDEX idx_transaction_subcategory_id ON transaction(subcategory_id);
CREATE INDEX idx_subcategory_category_id ON subcategory(category_id);
CREATE INDEX idx_category_user_id ON category(user_id);
CREATE INDEX idx_budget_user_id ON budget(user_id);
CREATE INDEX idx_budget_period_id ON budget(period_id);
CREATE INDEX idx_budget_period_user_id ON budget_period(user_id);
CREATE INDEX idx_budget_allocation_budget_id ON budget_allocation(budget_id);
CREATE INDEX idx_budget_allocation_subcategory_id ON budget_allocation(subcategory_id);
CREATE INDEX idx_income_source_budget_id ON income_source(budget_id);
CREATE INDEX idx_account_user_id ON account(user_id);
CREATE INDEX idx_recurring_income_user_id ON recurring_income_source(user_id);
CREATE INDEX idx_recurring_allocation_user_id ON recurring_budget_allocation(user_id);
CREATE INDEX idx_recurring_allocation_subcategory_id ON recurring_budget_allocation(subcategory_id);
CREATE INDEX idx_password_reset_user_id ON password_reset_token(user_id);
CREATE INDEX idx_email_verification_user_id ON email_verification(user_id);
```

### 1.2 Composite Indexes for Common Query Patterns

Based on codebase analysis, these composite indexes optimize the most frequent queries:

```sql
-- Transaction queries (most frequent)
CREATE INDEX idx_transaction_user_date ON transaction(user_id, transaction_date DESC);
CREATE INDEX idx_transaction_user_subcategory_date ON transaction(user_id, subcategory_id, transaction_date DESC);
CREATE INDEX idx_transaction_subcategory_date_range ON transaction(subcategory_id, transaction_date);

-- Budget period queries
CREATE INDEX idx_budget_period_user_active ON budget_period(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_budget_period_dates ON budget_period(start_date, end_date);

-- Category queries
CREATE INDEX idx_category_user_template ON category(user_id, is_template);
CREATE INDEX idx_subcategory_name_category ON subcategory(name, category_id); -- Already has unique constraint

-- Budget queries
CREATE INDEX idx_budget_user_period ON budget(user_id, period_id);

-- Account queries
CREATE INDEX idx_account_user_active ON account(user_id, is_active) WHERE is_active = TRUE;

-- Recurring items
CREATE INDEX idx_recurring_income_user_active ON recurring_income_source(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_recurring_allocation_user_active ON recurring_budget_allocation(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_recurring_allocation_subcategory_active ON recurring_budget_allocation(subcategory_id, is_active) WHERE is_active = TRUE;
```

### 1.3 Unique Indexes (Already Exist)

```sql
-- These are already defined as constraints, but ensure they exist as indexes
-- User table
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_username ON "user"(username);
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_email ON "user"(email);

-- Subcategory unique constraint
-- Already exists: CONSTRAINT uq_subcategory_name_category UNIQUE (name, category_id)
```

### 1.4 Partial Indexes for Filtered Queries

These indexes only include rows matching common WHERE clauses:

```sql
-- Active items only (reduces index size significantly)
CREATE INDEX idx_account_active ON account(user_id) WHERE is_active = TRUE;
CREATE INDEX idx_recurring_income_active ON recurring_income_source(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_recurring_allocation_active ON recurring_budget_allocation(user_id, subcategory_id) WHERE is_active = TRUE;
CREATE INDEX idx_budget_period_active ON budget_period(user_id) WHERE is_active = TRUE;
```

## 2. UUID vs Integer Primary Keys Analysis

### Recommendation: **Hybrid Approach**

- **Keep integers for internal tables**: User, Category, Subcategory, Budget, BudgetPeriod
  - **Pros**: Faster joins, smaller indexes, better performance
  - **Cons**: Sequential IDs can be enumerated (security concern)
  
- **Use UUIDs for user-facing identifiers**: Add a `uuid` column to User table
  - Generate UUIDs for API responses
  - Use integers for internal joins (performance)
  - Provides privacy/security benefits without performance hit

### Alternative: Full UUID Migration (If Privacy is Critical)

Only if you have strict privacy/security requirements:

**Pros:**
- Prevents ID enumeration attacks
- Easier distributed systems (if you scale horizontally later)
- More privacy-friendly

**Cons:**
- 16 bytes vs 4 bytes (4x storage overhead)
- Slower index lookups (UUIDs are random, not sequential)
- 10-15% slower joins on large tables
- Larger indexes = more memory usage

**Recommendation**: Don't use UUIDs for primary keys unless you have specific security/privacy requirements. The performance trade-off is significant at 100k users.

## 3. Table Partitioning Strategy

### 3.1 When to Partition

Partitioning is only beneficial when tables have:
- Millions of rows per partition
- Clear partition key (user_id in your case)
- Queries consistently filter by partition key

### 3.2 Recommendation: **Defer Partitioning**

At 100,000 users:
- Even if each user has 1,000 transactions = 100M rows
- PostgreSQL handles 100M rows efficiently with proper indexes
- Partitioning adds complexity and overhead

**Consider partitioning when:**
- Transaction table exceeds 500M-1B rows
- Queries become slow despite proper indexing
- You're running out of maintenance windows

### 3.3 If You Must Partition (Future Plan)

If you reach that scale, partition by user_id ranges:

```sql
-- Example: Range partitioning (when needed)
CREATE TABLE transaction_partitioned (
    LIKE transaction INCLUDING ALL
) PARTITION BY RANGE (user_id);

CREATE TABLE transaction_0_20000 PARTITION OF transaction_partitioned
    FOR VALUES FROM (1) TO (20001);
CREATE TABLE transaction_20000_40000 PARTITION OF transaction_partitioned
    FOR VALUES FROM (20001) TO (40001);
-- ... etc
```

**Better alternative**: Hash partitioning by user_id:
```sql
CREATE TABLE transaction_partitioned (
    LIKE transaction INCLUDING ALL
) PARTITION BY HASH (user_id);

CREATE TABLE transaction_part_0 PARTITION OF transaction_partitioned FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE transaction_part_1 PARTITION OF transaction_partitioned FOR VALUES WITH (MODULUS 8, REMAINDER 1);
-- ... 8 partitions total
```

## 4. Data Type Optimizations

### 4.1 Money Fields

```sql
-- Change FLOAT to NUMERIC for money (prevents rounding errors)
ALTER TABLE transaction ALTER COLUMN amount TYPE NUMERIC(12, 2);
ALTER TABLE budget_allocation ALTER COLUMN allocated_amount TYPE NUMERIC(12, 2);
ALTER TABLE income_source ALTER COLUMN amount TYPE NUMERIC(12, 2);
ALTER TABLE account ALTER COLUMN current_balance TYPE NUMERIC(12, 2);
-- etc.
```

### 4.2 Boolean Fields

PostgreSQL handles booleans natively (unlike SQLite storing as integers). Ensure they're defined as BOOLEAN.

### 4.3 Timestamps

Consider timezone-aware timestamps:
```sql
ALTER TABLE transaction ALTER COLUMN transaction_date TYPE TIMESTAMPTZ;
ALTER TABLE "user" ALTER COLUMN created_at TYPE TIMESTAMPTZ;
-- etc.
```

## 5. Query Optimization Strategies

### 5.1 Covering Indexes

These indexes contain all columns needed for a query, avoiding table lookups:

```sql
-- For transaction listing (user_id + transaction_date + amount)
CREATE INDEX idx_transaction_covering ON transaction(user_id, transaction_date DESC) 
    INCLUDE (amount, description, subcategory_id);

-- For budget summaries
CREATE INDEX idx_budget_allocation_covering ON budget_allocation(budget_id, subcategory_id) 
    INCLUDE (allocated_amount, is_recurring_allocation);
```

### 5.2 Materialized Views (For Reporting)

For expensive dashboard queries:

```sql
CREATE MATERIALIZED VIEW user_spending_summary AS
SELECT 
    user_id,
    subcategory_id,
    DATE_TRUNC('month', transaction_date) as month,
    SUM(ABS(amount)) as total_spent
FROM transaction
WHERE amount < 0
GROUP BY user_id, subcategory_id, DATE_TRUNC('month', transaction_date);

CREATE UNIQUE INDEX ON user_spending_summary(user_id, subcategory_id, month);

-- Refresh periodically or on-demand
REFRESH MATERIALIZED VIEW CONCURRENTLY user_spending_summary;
```

### 5.3 Query Pattern Improvements

In your code, use `select_related` equivalents:

```python
# Instead of:
transactions = Transaction.query.filter_by(user_id=user_id).all()
# Then accessing transaction.subcategory.category (N+1 queries)

# Use eager loading:
from sqlalchemy.orm import joinedload
transactions = Transaction.query.options(
    joinedload(Transaction.subcategory).joinedload(Subcategory.category)
).filter_by(user_id=user_id).all()
```

## 6. Connection Pooling and Caching

### 6.1 Connection Pooling

Ensure SQLAlchemy connection pool is configured:
```python
# In config
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 3600
}
```

### 6.2 Query Result Caching

For frequently accessed, rarely changing data:
- User settings (currency, theme)
- Category/Subcategory lists (cache per user)
- Active budget period info

Consider Redis or application-level caching.

## 7. Maintenance and Monitoring

### 7.1 Regular Maintenance

```sql
-- Update statistics for query planner
ANALYZE;

-- Vacuum to reclaim space (auto-vacuum should handle this)
VACUUM ANALYZE;

-- Rebuild indexes if needed (rarely)
REINDEX DATABASE wealthwise;
```

### 7.2 Monitoring Queries

```sql
-- Find slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 20;

-- Find missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY abs(correlation) DESC;
```

## 8. Implementation Priority

1. **Phase 1 (Immediate - Highest Impact)**:
   - Add all foreign key indexes
   - Add composite indexes on user_id + date/user_id + active
   - Change FLOAT to NUMERIC for money

2. **Phase 2 (Before 50k users)**:
   - Add covering indexes
   - Optimize queries with eager loading
   - Implement connection pooling

3. **Phase 3 (Before 100k users)**:
   - Add materialized views for reporting
   - Implement caching layer
   - Monitor and tune based on actual usage

4. **Phase 4 (If needed at 500k+ users)**:
   - Consider partitioning
   - Horizontal scaling considerations
   - Database sharding (if needed)

## 9. Expected Performance

With these optimizations:

- **Query Times**:
  - User dashboard: < 50ms (with proper indexes)
  - Transaction listing: < 100ms (even with 10k transactions per user)
  - Budget calculations: < 200ms
  
- **Scalability**:
  - 100k users: Excellent performance
  - 500k users: Still good, may need partitioning
  - 1M+ users: Partitioning + caching critical

## 10. Migration Steps

1. Create indexes (non-blocking, can run during low traffic)
2. Change data types (requires table locks - plan downtime)
3. Add UUID columns if needed (non-blocking)
4. Test with production-like data volumes
5. Monitor query performance after each phase

## Conclusion

**Skip UUID primary keys** - use integers for performance
**Skip partitioning now** - add indexes first
**Focus on indexing** - 80% of performance gain comes from proper indexes
**Monitor and iterate** - adjust based on actual query patterns

This strategy gives you the best performance-to-complexity ratio for 100,000 users.

