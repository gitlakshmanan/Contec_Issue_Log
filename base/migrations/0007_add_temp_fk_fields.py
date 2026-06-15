# Add temporary foreign key fields to Issue model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_seed_lookup_data'),
    ]

    operations = [
        # Add temporary nullable FK fields
        migrations.AddField(
            model_name='issue',
            name='customer_fk',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='issues_temp',
                to='base.customer',
                verbose_name='Customer FK'
            ),
        ),
        migrations.AddField(
            model_name='issue',
            name='issue_cat_fk',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='issues_temp',
                to='base.issuecategory',
                verbose_name='Issue Category FK'
            ),
        ),
        migrations.AddField(
            model_name='issue',
            name='impact_category_fk',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='issues_temp',
                to='base.impactcategory',
                verbose_name='Impact Category FK'
            ),
        ),
        migrations.AddField(
            model_name='issue',
            name='impacted_customer_text',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='Impacted Customers Text'
            ),
        ),
    ]
