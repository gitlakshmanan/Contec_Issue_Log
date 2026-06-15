# Generated manually for adding department and job_name fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contec_cr', '0002_changerequest_cr_approved_by_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='changerequest',
            name='department',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='changerequest',
            name='job_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]