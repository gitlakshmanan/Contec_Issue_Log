"""
Management command to seed initial data for lookup tables
Usage: python manage.py seed_lookup_tables
"""

from django.core.management.base import BaseCommand
from base.models import Customer, IssueCategory, ImpactCategory


class Command(BaseCommand):
    help = 'Seeds initial data for Customer, IssueCategory, and ImpactCategory lookup tables'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to seed lookup tables...'))
        
        # Seed Customers
        customers_data = [
            {'name': 'Mediacom', 'code': 'MDC', 'description': 'Mediacom Communications Corporation'},
            {'name': 'Midco', 'code': 'MID', 'description': 'Midcontinent Communications'},
            {'name': 'Frontier', 'code': 'FTR', 'description': 'Frontier Communications'},
            {'name': 'Roku', 'code': 'RKU', 'description': 'Roku, Inc.'},
        ]
        
        customer_count = 0
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(
                name=data['name'],
                defaults={
                    'code': data['code'],
                    'description': data['description'],
                    'is_active': True
                }
            )
            if created:
                customer_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created customer: {customer.name}'))
            else:
                self.stdout.write(f'  - Customer already exists: {customer.name}')
        
        # Seed Issue Categories (5M Framework)
        issue_categories_data = [
            {
                'name': 'Man Error',
                'code': 'MAN',
                'description': 'Human-related errors including training, skills, and procedural mistakes'
            },
            {
                'name': 'Machine Error',
                'code': 'MCH',
                'description': 'Equipment, hardware, or system failures and malfunctions'
            },
            {
                'name': 'Material Error',
                'code': 'MAT',
                'description': 'Issues related to raw materials, components, or supplies'
            },
            {
                'name': 'Method Error',
                'code': 'MTH',
                'description': 'Process, procedure, or methodology-related issues'
            },
            {
                'name': 'Measurement Error',
                'code': 'MSR',
                'description': 'Data collection, metrics, or measurement accuracy issues'
            },
        ]
        
        category_count = 0
        for data in issue_categories_data:
            category, created = IssueCategory.objects.get_or_create(
                name=data['name'],
                defaults={
                    'code': data['code'],
                    'description': data['description'],
                    'is_active': True
                }
            )
            if created:
                category_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created issue category: {category.name}'))
            else:
                self.stdout.write(f'  - Issue category already exists: {category.name}')
        
        # Seed Impact Categories
        impact_categories_data = [
            {
                'name': 'Undercharge',
                'code': 'UND',
                'description': 'Customer was charged less than the correct amount'
            },
            {
                'name': 'Overcharge',
                'code': 'OVR',
                'description': 'Customer was charged more than the correct amount'
            },
            {
                'name': 'Credit',
                'code': 'CRD',
                'description': 'Credit issued to customer account'
            },
            {
                'name': 'Debit',
                'code': 'DBT',
                'description': 'Debit applied to customer account'
            },
        ]
        
        impact_count = 0
        for data in impact_categories_data:
            impact, created = ImpactCategory.objects.get_or_create(
                name=data['name'],
                defaults={
                    'code': data['code'],
                    'description': data['description'],
                    'is_active': True
                }
            )
            if created:
                impact_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created impact category: {impact.name}'))
            else:
                self.stdout.write(f'  - Impact category already exists: {impact.name}')
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  • Customers created: {customer_count}'))
        self.stdout.write(self.style.SUCCESS(f'  • Issue Categories created: {category_count}'))
        self.stdout.write(self.style.SUCCESS(f'  • Impact Categories created: {impact_count}'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Next steps:'))
        self.stdout.write('  1. Run migrations: python manage.py makemigrations && python manage.py migrate')
        self.stdout.write('  2. Access Django admin to manage lookup tables')
        self.stdout.write('  3. Users can now add new customers, categories, and impacts via admin interface')
