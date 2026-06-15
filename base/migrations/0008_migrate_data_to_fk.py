# Migrate existing data from CharField to ForeignKey

from django.db import migrations


def migrate_to_foreign_keys(apps, schema_editor):
    """Migrate existing string values to foreign key relationships"""
    Issue = apps.get_model('base', 'Issue')
    Customer = apps.get_model('base', 'Customer')
    IssueCategory = apps.get_model('base', 'IssueCategory')
    ImpactCategory = apps.get_model('base', 'ImpactCategory')
    
    # Mapping for old string values to new objects
    customer_map = {
        'Mediacom': Customer.objects.get(name='Mediacom'),
        'Midco': Customer.objects.get(name='Midco'),
        'Frontier': Customer.objects.get(name='Frontier'),
    }
    
    category_map = {
        'ManError': IssueCategory.objects.get(name='Man Error'),
        'MachineError': IssueCategory.objects.get(name='Machine Error'),
        'MaterialError': IssueCategory.objects.get(name='Material Error'),
        'MethodError': IssueCategory.objects.get(name='Method Error'),
        'MeasureableError': IssueCategory.objects.get(name='Measurement Error'),
    }
    
    impact_map = {
        'Undercharge': ImpactCategory.objects.get(name='Undercharge'),
        'Overcharge': ImpactCategory.objects.get(name='Overcharge'),
        'Credit': ImpactCategory.objects.get(name='Credit'),
        'Debit': ImpactCategory.objects.get(name='Debit'),
    }
    
    # Migrate all existing issues
    for issue in Issue.objects.all():
        # Migrate customer
        if issue.customer in customer_map:
            issue.customer_fk = customer_map[issue.customer]
        
        # Migrate issue category
        if issue.issue_cat in category_map:
            issue.issue_cat_fk = category_map[issue.issue_cat]
        
        # Migrate impact category
        if issue.impact_category and issue.impact_category in impact_map:
            issue.impact_category_fk = impact_map[issue.impact_category]
        
        # Migrate impacted customer (from dropdown to text)
        if issue.impacted_customer:
            issue.impacted_customer_text = issue.impacted_customer
        
        issue.save()


def reverse_migration(apps, schema_editor):
    """Reverse the data migration"""
    Issue = apps.get_model('base', 'Issue')
    
    # Clear the FK fields
    Issue.objects.all().update(
        customer_fk=None,
        issue_cat_fk=None,
        impact_category_fk=None,
        impacted_customer_text=None
    )


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_add_temp_fk_fields'),
    ]

    operations = [
        migrations.RunPython(migrate_to_foreign_keys, reverse_migration),
    ]
