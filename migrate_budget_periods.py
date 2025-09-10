#!/usr/bin/env python3
"""
Migration script to add BudgetPeriod table and update existing Budget table
This script handles the transition from month_year based budgets to period-based budgets
"""

import sqlite3
import os
from datetime import datetime, timedelta

def migrate_database():
    db_path = 'instance/wealthwise.db'
    
    if not os.path.exists(db_path):
        print("Database not found. Please run the app first to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting database migration...")
        
        # Check if BudgetPeriod table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='budget_period'")
        if cursor.fetchone():
            print("BudgetPeriod table already exists. Migration may have been run already.")
            return
        
        # Create BudgetPeriod table
        print("Creating BudgetPeriod table...")
        cursor.execute('''
            CREATE TABLE budget_period (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                period_type VARCHAR(20) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                user_id INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        
        # Add period_id column to Budget table
        print("Adding period_id column to Budget table...")
        cursor.execute('ALTER TABLE budget ADD COLUMN period_id INTEGER')
        cursor.execute('ALTER TABLE budget ADD COLUMN FOREIGN KEY (period_id) REFERENCES budget_period (id)')
        
        # Migrate existing budgets to use periods
        print("Migrating existing budgets...")
        cursor.execute('SELECT id, month_year, user_id FROM budget')
        existing_budgets = cursor.fetchall()
        
        for budget_id, month_year, user_id in existing_budgets:
            # Parse month_year (YYYY-MM format)
            year, month = month_year.split('-')
            start_date = f"{year}-{month}-01"
            
            # Calculate end date (last day of month)
            if month == '12':
                next_month = f"{int(year)+1}-01-01"
            else:
                next_month = f"{year}-{int(month)+1:02d}-01"
            
            end_date = (datetime.strptime(next_month, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Create period for this budget
            period_name = datetime.strptime(month_year, '%Y-%m').strftime('%B %Y')
            cursor.execute('''
                INSERT INTO budget_period (name, period_type, start_date, end_date, user_id, is_active)
                VALUES (?, 'monthly', ?, ?, ?, 1)
            ''', (period_name, start_date, end_date, user_id))
            
            period_id = cursor.lastrowid
            
            # Update budget to reference the period
            cursor.execute('UPDATE budget SET period_id = ? WHERE id = ?', (period_id, budget_id))
        
        # Remove month_year column (SQLite doesn't support DROP COLUMN, so we'll leave it for now)
        print("Migration completed successfully!")
        
        conn.commit()
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
