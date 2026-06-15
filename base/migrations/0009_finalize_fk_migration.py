# Finalize migration by removing old fields and renaming new ones

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_migrate_data_to_fk'),
    ]

    operations = [
        # Remove old CharField fields
        migrations.RemoveField(
            model_name='issue',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='issue_cat',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='impact_category',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='impacted_customer',
        ),
        
        # Rename temporary FK fields to final names
        migrations.RenameField(
            model_name='issue',
            old_name='customer_fk',
            new_name='customer',
        ),
        migrations.RenameField(
            model_name='issue',
            old_name='issue_cat_fk',
            new_name='issue_cat',
        ),
        migrations.RenameField(
            model_name='issue',
            old_name='impact_category_fk',
            new_name='impact_category',
        ),
        migrations.RenameField(
            model_name='issue',
            old_name='impacted_customer_text',
            new_name='impacted_customer',
        ),
        
        # Make customer and issue_cat required (NOT NULL)
        migrations.AlterField(
            model_name='issue',
            name='customer',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='issues',
                to='base.customer',
                verbose_name='Customer',
                help_text='Select the customer associated with this issue'
            ),
        ),
        migrations.AlterField(
            model_name='issue',
            name='issue_cat',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='issues',
                to='base.issuecategory',
                verbose_name='Issue Category',
                help_text='Select the issue category (5M Framework)'
            ),
        ),
        migrations.AlterField(
            model_name='issue',
            name='impact_category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='issues',
                to='base.impactcategory',
                verbose_name='Impact Category',
                help_text='Select the financial impact category'
            ),
        ),
        migrations.AlterField(
            model_name='issue',
            name='impacted_customer',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='Impacted Customers',
                help_text='Enter impacted customer names (free text)'
            ),
        ),
    ]
