from django.db import migrations, models


def convert_bool_to_yesno(apps, schema_editor):
    Issue = apps.get_model('base', 'Issue')
    for issue in Issue.objects.all():
        # convert existing boolean-like fields to 'Yes'/'No'
        try:
            # customer_received and rebilled_credited previously were booleans
            cr = getattr(issue, 'customer_received', None)
            if isinstance(cr, bool):
                issue.customer_received = 'Yes' if cr else 'No'
        except Exception:
            pass
        try:
            rc = getattr(issue, 'rebilled_credited', None)
            if isinstance(rc, bool):
                issue.rebilled_credited = 'Yes' if rc else 'No'
        except Exception:
            pass
        issue.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_add_rebill_proof'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='department',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Department', help_text='Department responsible for this issue'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='customer_received',
            field=models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='No', help_text="Whether the customer has received the invoice/notice (Yes/No)", max_length=3, verbose_name='Customer Received'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='rebilled_credited',
            field=models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='No', help_text="Indicates if this issue was rebilled or credited (Yes/No)", max_length=3, verbose_name='Rebilled/Credited'),
        ),
        migrations.RunPython(convert_bool_to_yesno, reverse_code=migrations.RunPython.noop),
    ]
