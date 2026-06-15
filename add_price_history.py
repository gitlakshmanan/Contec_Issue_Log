import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
django.setup()

from price_book.models import Customer, PartPrice, PONumber, SONumber
from django.contrib.auth.models import User
from datetime import date, timedelta

print("=" * 60)
print("Adding Price History Test Data")
print("=" * 60)

user = User.objects.first()
customer = Customer.objects.get(name='Customer A')

# Create PO and SO numbers
po1, _ = PONumber.objects.get_or_create(po_number='PO-2024-001')
po2, _ = PONumber.objects.get_or_create(po_number='PO-2024-002')
po3, _ = PONumber.objects.get_or_create(po_number='PO-2025-001')

so1, _ = SONumber.objects.get_or_create(so_number='SO-2024-001')
so2, _ = SONumber.objects.get_or_create(so_number='SO-2024-002')
so3, _ = SONumber.objects.get_or_create(so_number='SO-2025-001')

# Create price history for PART-001
prices = [
    {
        'price': 80.00,
        'margin': 10.0,
        'startdate': date(2024, 1, 1),
        'enddate': date(2024, 6, 30),
        'po': po1,
        'so': so1,
        'remarks': 'Initial price for 2024 H1'
    },
    {
        'price': 90.00,
        'margin': 12.0,
        'startdate': date(2024, 7, 1),
        'enddate': date(2024, 12, 31),
        'po': po2,
        'so': so2,
        'remarks': 'Price increase for 2024 H2'
    },
    {
        'price': 100.00,
        'margin': 15.0,
        'startdate': date(2025, 1, 1),
        'enddate': None,  # Current price - no end date
        'po': po3,
        'so': so3,
        'remarks': 'Current price for 2025'
    },
]

for price_data in prices:
    part, created = PartPrice.objects.get_or_create(
        partnumber='PART-001',
        customer=customer,
        startdate=price_data['startdate'],
        defaults={
            'price': price_data['price'],
            'margin': price_data['margin'],
            'enddate': price_data['enddate'],
            'po_number': price_data['po'],
            'so_number': price_data['so'],
            'remarks': price_data['remarks'],
            'created_by': user,
            'status': 'approved',
            'is_active': True
        }
    )
    if created:
        print(f"Created: PART-001 @ ${price_data['price']} ({price_data['startdate']} to {price_data['enddate'] or 'Ongoing'})")

print("=" * 60)
print("\nPrice history created successfully!")
print("\nNow visit: http://127.0.0.1:8000/parts/")
print("Click on PART-001 to see the price history")
print("The current price ($100.00) will be highlighted in GREEN")
print("=" * 60)
