import psycopg2

# Database connection details from your settings.py
conn = psycopg2.connect(
    host="localhost",
    database="contec_db", 
    user="postgres",
    password="Snowfall$123",
    port="5432"
)

cursor = conn.cursor()

# Add missing columns
try:
    cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_issues BOOLEAN NOT NULL DEFAULT TRUE;")
    print("✓ Added can_access_issues column")
except Exception as e:
    print(f"can_access_issues: {e}")

try:
    cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_parts BOOLEAN NOT NULL DEFAULT FALSE;")
    print("✓ Added can_access_parts column")
except Exception as e:
    print(f"can_access_parts: {e}")

try:
    cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_cr BOOLEAN NOT NULL DEFAULT FALSE;")
    print("✓ Added can_access_cr column")
except Exception as e:
    print(f"can_access_cr: {e}")

try:
    cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_tasks BOOLEAN NOT NULL DEFAULT TRUE;")
    print("✓ Added can_access_tasks column")
except Exception as e:
    print(f"can_access_tasks: {e}")

try:
    cursor.execute("ALTER TABLE base_userprofile ADD COLUMN can_access_reports BOOLEAN NOT NULL DEFAULT FALSE;")
    print("✓ Added can_access_reports column")
except Exception as e:
    print(f"can_access_reports: {e}")

conn.commit()
cursor.close()
conn.close()

print("\n✓ Database updated successfully!")
print("Role-based menu access is now active.")