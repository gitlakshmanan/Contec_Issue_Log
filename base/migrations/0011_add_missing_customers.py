# Migration to add missing customers from original CUSTOMER_CHOICES

from django.db import migrations


def add_missing_customers(apps, schema_editor):
    """Add missing customers from original CUSTOMER_CHOICES"""
    Customer = apps.get_model('base', 'Customer')
    
    # Missing customers from original CUSTOMER_CHOICES
    missing_customers_data = [
        {'name': 'Astound', 'code': 'AST', 'description': 'Astound Broadband'},
        {'name': 'Breezeline', 'code': 'BRZ', 'description': 'Breezeline Communications'},
        {'name': 'Cableone', 'code': 'C1', 'description': 'Cable One'},
        {'name': 'Tivo', 'code': 'TVO', 'description': 'TiVo Corporation'},
        {'name': 'Ziply', 'code': 'ZIP', 'description': 'Ziply Fiber'},
    ]
    
    for data in missing_customers_data:
        Customer.objects.get_or_create(
            name=data['name'],
            defaults={
                'code': data['code'],
                'description': data['description'],
                'is_active': True
            }
        )
    
    # Update existing Midco to Midcontinent to match original choices
    try:
        midco = Customer.objects.get(name='Midco')
        midco.name = 'Midcontinent'
        midco.save()
    except Customer.DoesNotExist:
        pass


def reverse_add_customers(apps, schema_editor):
    """Remove the added customers if migration is reversed"""
    Customer = apps.get_model('base', 'Customer')
    
    customer_names = ['Astound', 'Breezeline', 'Cableone', 'Tivo', 'Ziply']
    Customer.objects.filter(name__in=customer_names).delete()
    
    # Revert Midcontinent back to Midco
    try:
        midcontinent = Customer.objects.get(name='Midcontinent')
        midcontinent.name = 'Midco'
        midcontinent.save()
    except Customer.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_issue_attachment'),
    ]

    operations = [
        migrations.RunPython(add_missing_customers, reverse_add_customers),
    ]