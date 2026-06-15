import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
django.setup()

from price_book.models import Customer, PartPrice
from django.contrib.auth.models import User
from datetime import date

print("=" * 50)
print("Adding Sample Data to Parts Price Manager")
print("=" * 50)

# Get or create a user
user = User.objects.first()
if not user:
    user = User.objects.create_user('admin', 'admin@example.com', 'admin')
    print(f"Created user: {user.username}")
else:
    print(f"Using existing user: {user.username}")

# Create sample customers
customers_data = ['Customer A', 'Customer B', 'Customer C']
for cust_name in customers_data:
    customer, created = Customer.objects.get_or_create(name=cust_name)
    if created:
        print(f"Created customer: {cust_name}")

# Create sample parts
parts_data = [
    {'partnumber': 'PART-001', 'price': 100.00, 'margin': 15.0, 'customer': 'Customer A'},
    {'partnumber': 'PART-002', 'price': 250.50, 'margin': 20.0, 'customer': 'Customer B'},
    {'partnumber': 'PART-003', 'price': 75.25, 'margin': 10.0, 'customer': 'Customer C'},
]

for part_data in parts_data:
    customer = Customer.objects.get(name=part_data['customer'])
    part, created = PartPrice.objects.get_or_create(
        partnumber=part_data['partnumber'],
        customer=customer,
        defaults={
            'price': part_data['price'],
            'margin': part_data['margin'],
            'startdate': date.today(),
            'created_by': user,
            'status': 'approved',
            'is_active': True
        }
    )
    if created:
        print(f"Created part: {part_data['partnumber']} - ${part_data['price']}")

print("=" * 50)
print(f"\nTotal Parts: {PartPrice.objects.filter(is_active=True).count()}")
print("\nNow refresh your dashboard at:")
print("http://127.0.0.1:8000/dashboard/")
print("\nThe Parts Price Manager card should show: 3")
print("=" * 50)
