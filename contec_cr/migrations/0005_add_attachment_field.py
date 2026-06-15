# Generated manually for adding attachment field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contec_cr', '0004_add_priority_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='changerequest',
            name='attachment',
            field=models.FileField(
                blank=True,
                help_text='Upload documents (.pdf, .docx, .xlsx, .txt) up to 5MB',
                null=True,
                upload_to='cr_attachments/%Y/%m/',
                verbose_name='Attachment'
            ),
        ),
    ]