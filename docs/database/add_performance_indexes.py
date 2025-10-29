"""
Database migration script to add performance indexes for scalability.

Run this after migrating to PostgreSQL:
    python -m migrations.add_performance_indexes
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/wealthwise')

def add_indexes():
    """Add all performance indexes."""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    indexes = [
        # Foreign key indexes (critical for joins)
        "CREATE INDEX IF NOT EXISTS idx_transaction_user_id ON transaction(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_transaction_subcategory_id ON transaction(subcategory_id)",
        "CREATE INDEX IF NOT EXISTS idx_subcategory_category_id ON subcategory(category_id)",
        "CREATE INDEX IF NOT EXISTS idx_category_user_id ON category(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_budget_user_id ON budget(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_budget_period_id ON budget(period_id)",
        "CREATE INDEX IF NOT EXISTS idx_budget_period_user_id ON budget_period(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_budget_allocation_budget_id ON budget_allocation(budget_id)",
        "CREATE INDEX IF NOT EXISTS idx_budget_allocation_subcategory_id ON budget_allocation(subcategory_id)",
        "CREATE INDEX IF NOT EXISTS idx_income_source_budget_id ON income_source(budget_id)",
        "CREATE INDEX IF NOT EXISTS idx_account_user_id ON account(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_recurring_income_user_id ON recurring_income_source(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_recurring_allocation_user_id ON recurring_budget_allocation(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_recurring_allocation_subcategory_id ON recurring_budget_allocation(subcategory_id)",
        "CREATE INDEX IF NOT EXISTS idx_password_reset_user_id ON password_reset_token(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_email_verification_user_id ON email_verification(user_id)",
        
        # Composite indexes for common query patterns
        "CREATE INDEX IF NOT EXISTS idx_transaction_user_date ON transaction(user_id, transaction_date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_transaction_user_subcategory_date ON transaction(user_id, subcategory_id, transaction_date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_transaction_subcategory_date_range ON transaction(subcategory_id, transaction_date)",
        
        "CREATE INDEX IF NOT EXISTS idx_budget_period_user_active ON budget_period(user_id, is_active) WHERE is_active = TRUE",
        "CREATE INDEX IF NOT EXISTS idx_budget_user_period ON budget(user_id, period_id)",
        
        "CREATE INDEX IF NOT EXISTS idx_category_user_template ON category(user_id, is_template)",
        
        "CREATE INDEX IF NOT EXISTS idx_account_user_active ON account(user_id, is_active) WHERE is_active = TRUE",
        
        "CREATE INDEX IF NOT EXISTS idx_recurring_income_user_active ON recurring_income_source(user_id, is_active) WHERE is_active = TRUE",
        "CREATE INDEX IF NOT EXISTS idx_recurring_allocation_user_active ON recurring_budget_allocation(user_id, is_active) WHERE is_active = TRUE",
        
        # Token indexes for quick lookups
        "CREATE INDEX IF NOT EXISTS idx_password_reset_token ON password_reset_token(token) WHERE used = FALSE",
        "CREATE INDEX IF NOT EXISTS idx_email_verification_token ON email_verification(token) WHERE verified = FALSE",
    ]
    
    print("Adding performance indexes...")
    for idx_sql in indexes:
        try:
            session.execute(text(idx_sql))
            session.commit()
            print(f"✓ Created index: {idx_sql.split('ON ')[1].split()[0]}")
        except Exception as e:
            print(f"✗ Error creating index: {e}")
            session.rollback()
    
    print("\n✓ Index creation complete!")
    print("\nNext steps:")
    print("1. Run ANALYZE; to update query planner statistics")
    print("2. Monitor query performance with EXPLAIN ANALYZE")
    print("3. Check pg_stat_user_indexes for index usage")

if __name__ == '__main__':
    add_indexes()

