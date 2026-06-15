from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_userprofile_show_tips'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='rebill_proof',
            field=models.TextField(blank=True, null=True, help_text='Details or proof for rebill/credit (invoice #, transaction ref, notes)', verbose_name='Rebill/Credit Proof'),
        ),
    ]
