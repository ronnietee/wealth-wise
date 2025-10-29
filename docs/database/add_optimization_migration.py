"""
Flask-Migrate migration template for database optimizations.

To create actual migration:
    flask db migrate -m "Add performance indexes and optimize data types"

Then edit the generated migration file to include all optimizations.
"""

# This is a template. Actual migrations should be generated via Flask-Migrate.
# Use: flask db migrate -m "Add indexes and optimize schema"

"""
Example migration content (paste into generated migration file):

def upgrade():
    # Add foreign key indexes
    op.create_index('idx_transaction_user_id', 'transaction', ['user_id'])
    op.create_index('idx_transaction_subcategory_id', 'transaction', ['subcategory_id'])
    op.create_index('idx_subcategory_category_id', 'subcategory', ['category_id'])
    op.create_index('idx_category_user_id', 'category', ['user_id'])
    op.create_index('idx_budget_user_id', 'budget', ['user_id'])
    op.create_index('idx_budget_period_id', 'budget', ['period_id'])
    op.create_index('idx_budget_period_user_id', 'budget_period', ['user_id'])
    op.create_index('idx_budget_allocation_budget_id', 'budget_allocation', ['budget_id'])
    op.create_index('idx_budget_allocation_subcategory_id', 'budget_allocation', ['subcategory_id'])
    op.create_index('idx_income_source_budget_id', 'income_source', ['budget_id'])
    op.create_index('idx_account_user_id', 'account', ['user_id'])
    op.create_index('idx_recurring_income_user_id', 'recurring_income_source', ['user_id'])
    op.create_index('idx_recurring_allocation_user_id', 'recurring_budget_allocation', ['user_id'])
    op.create_index('idx_recurring_allocation_subcategory_id', 'recurring_budget_allocation', ['subcategory_id'])
    
    # Add composite indexes
    op.create_index('idx_transaction_user_date', 'transaction', ['user_id', op.desc('transaction_date')])
    op.create_index('idx_transaction_user_subcategory_date', 'transaction', ['user_id', 'subcategory_id', op.desc('transaction_date')])
    op.create_index('idx_budget_period_user_active', 'budget_period', ['user_id', 'is_active'])
    op.create_index('idx_budget_user_period', 'budget', ['user_id', 'period_id'])
    
    # Note: Data type changes (FLOAT to NUMERIC) should be done carefully
    # Example:
    # op.alter_column('transaction', 'amount', type_=sa.Numeric(12, 2))
    # Convert existing data:
    # op.execute("UPDATE transaction SET amount = amount::numeric(12, 2)")
    
    # Analyze to update statistics
    op.execute('ANALYZE')

def downgrade():
    # Drop indexes in reverse order
    op.drop_index('idx_budget_user_period', 'budget')
    op.drop_index('idx_budget_period_user_active', 'budget_period')
    op.drop_index('idx_transaction_user_subcategory_date', 'transaction')
    op.drop_index('idx_transaction_user_date', 'transaction')
    # ... drop all indexes
"""

