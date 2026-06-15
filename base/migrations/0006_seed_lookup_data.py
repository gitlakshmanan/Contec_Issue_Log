# Data migration to seed initial lookup table data

from django.db import migrations


def seed_lookup_tables(apps, schema_editor):
    """Populate initial data for lookup tables"""
    Customer = apps.get_model('base', 'Customer')
    IssueCategory = apps.get_model('base', 'IssueCategory')
    ImpactCategory = apps.get_model('base', 'ImpactCategory')
    
    # Seed Customers
    customers_data = [
        {'name': 'Mediacom', 'code': 'MDC', 'description': 'Mediacom Communications Corporation'},
        {'name': 'Midco', 'code': 'MID', 'description': 'Midcontinent Communications'},
        {'name': 'Frontier', 'code': 'FTR', 'description': 'Frontier Communications'},
    ]
    
    for data in customers_data:
        Customer.objects.get_or_create(
            name=data['name'],
            defaults={
                'code': data['code'],
                'description': data['description'],
                'is_active': True
            }
        )
    
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
    
    for data in issue_categories_data:
        IssueCategory.objects.get_or_create(
            name=data['name'],
            defaults={
                'code': data['code'],
                'description': data['description'],
                'is_active': True
            }
        )
    
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
    
    for data in impact_categories_data:
        ImpactCategory.objects.get_or_create(
            name=data['name'],
            defaults={
                'code': data['code'],
                'description': data['description'],
                'is_active': True
            }
        )


def reverse_seed(apps, schema_editor):
    """Remove seeded data if migration is reversed"""
    Customer = apps.get_model('base', 'Customer')
    IssueCategory = apps.get_model('base', 'IssueCategory')
    ImpactCategory = apps.get_model('base', 'ImpactCategory')
    
    Customer.objects.all().delete()
    IssueCategory.objects.all().delete()
    ImpactCategory.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_create_lookup_tables'),
    ]

    operations = [
        migrations.RunPython(seed_lookup_tables, reverse_seed),
    ]
