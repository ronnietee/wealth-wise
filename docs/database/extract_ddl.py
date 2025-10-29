#!/usr/bin/env python3
"""
Script to extract DDL (Data Definition Language) from SQLite database
for migration to PostgreSQL.
"""

import sqlite3
import sys
from pathlib import Path

def extract_ddl(db_path):
    """Extract DDL statements from SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("-- SQLite DDL Export")
    print(f"-- Database: {db_path}")
    print("-- Generated for PostgreSQL migration")
    print()
    print("-- Note: This DDL needs manual adjustments for PostgreSQL")
    print("-- See MIGRATION_GUIDE.md for conversion details")
    print()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    ddl_statements = []
    
    for (table_name,) in tables:
        # Skip SQLite system tables
        if table_name.startswith('sqlite_') or table_name == 'alembic_version':
            continue
        
        # Get CREATE TABLE statement
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()
        
        if result and result[0]:
            sql = result[0]
            ddl_statements.append(f"-- Table: {table_name}")
            ddl_statements.append(sql)
            ddl_statements.append(";")
            ddl_statements.append("")
            
            # Get indexes
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL", (table_name,))
            indexes = cursor.fetchall()
            
            for (index_sql,) in indexes:
                if index_sql and 'sqlite_autoindex' not in index_sql:
                    ddl_statements.append(f"-- Index for {table_name}")
                    ddl_statements.append(index_sql)
                    ddl_statements.append(";")
                    ddl_statements.append("")
    
    conn.close()
    
    return "\n".join(ddl_statements)

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'instance/wealthwise_dev.db'
    
    if not Path(db_path).exists():
        print(f"Error: Database file not found: {db_path}")
        sys.exit(1)
    
    ddl = extract_ddl(db_path)
    print(ddl)
    
    # Also save to file
    output_file = 'sqlite_ddl_export.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ddl)
    
    print(f"\n-- DDL saved to {output_file}", file=sys.stderr)

