#!/usr/bin/env python
"""
Script to add missing menu permission columns using Django's database connection.
Run this from the project root: python add_menu_permissions.py
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

def add_menu_permissions():
    """Add the missing menu permission columns"""
    with connection.cursor() as cursor:
        try:
            cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_issues BOOLEAN NOT NULL DEFAULT TRUE;")
            print("✓ Added can_access_issues column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ can_access_issues column already exists")
            else:
                print(f"✗ Error adding can_access_issues: {e}")

        try:
            cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_parts BOOLEAN NOT NULL DEFAULT FALSE;")
            print("✓ Added can_access_parts column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ can_access_parts column already exists")
            else:
                print(f"✗ Error adding can_access_parts: {e}")

        try:
            cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_cr BOOLEAN NOT NULL DEFAULT FALSE;")
            print("✓ Added can_access_cr column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ can_access_cr column already exists")
            else:
                print(f"✗ Error adding can_access_cr: {e}")

        try:
            cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_tasks BOOLEAN NOT NULL DEFAULT TRUE;")
            print("✓ Added can_access_tasks column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ can_access_tasks column already exists")
            else:
                print(f"✗ Error adding can_access_tasks: {e}")

        try:
            cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_reports BOOLEAN NOT NULL DEFAULT FALSE;")
            print("✓ Added can_access_reports column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ can_access_reports column already exists")
            else:
                print(f"✗ Error adding can_access_reports: {e}")

    print("\n✓ Menu permission columns added successfully!")
    print("Role-based menu access is now active.")

if __name__ == "__main__":
    add_menu_permissions()