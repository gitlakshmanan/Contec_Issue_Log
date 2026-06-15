# Generated manually for adding priority field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contec_cr', '0003_add_department_job_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='changerequest',
            name='priority',
            field=models.CharField(
                choices=[
                    ('high', 'High'),
                    ('medium', 'Medium'),
                    ('low', 'Low'),
                    ('planned_medium', 'Planned-Medium'),
                    ('planned_low', 'Planned-Low'),
                    ('unplanned_high', 'Un-Planned-High')
                ],
                default='medium',
                max_length=20
            ),
        ),
    ]