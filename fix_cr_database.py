#!/usr/bin/env python
"""
Script to manually apply the missing CR model changes to the database.
Run this from the project root directory: python fix_cr_database.py
"""

import os
import sys
import django
from django.db import connection

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
django.setup()

def apply_cr_changes():
    """Apply the missing database changes for CR model"""
    with connection.cursor() as cursor:
        try:
            # Add department column
            cursor.execute("ALTER TABLE contec_cr_changerequest ADD COLUMN department VARCHAR(100) NULL;")
            print("✓ Added department column")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("✓ Department column already exists")
            else:
                print(f"✗ Error adding department column: {e}")

        try:
            # Add job_name column
            cursor.execute("ALTER TABLE contec_cr_changerequest ADD COLUMN job_name VARCHAR(100) NULL;")
            print("✓ Added job_name column")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("✓ Job_name column already exists")
            else:
                print(f"✗ Error adding job_name column: {e}")

        try:
            # Add priority column
            cursor.execute("ALTER TABLE contec_cr_changerequest ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium';")
            print("✓ Added priority column")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("✓ Priority column already exists")
            else:
                print(f"✗ Error adding priority column: {e}")

    print("\n✓ Database changes applied successfully!")
    print("You can now access the CR approvals page without errors.")

if __name__ == "__main__":
    apply_cr_changes()