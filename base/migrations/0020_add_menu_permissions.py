# Generated manually for adding menu access permissions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_userprofile_can_access_approvals'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='can_access_issues',
            field=models.BooleanField(default=True, verbose_name='Can Access Issues'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='can_access_parts',
            field=models.BooleanField(default=False, verbose_name='Can Access Parts Price Book'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='can_access_cr',
            field=models.BooleanField(default=False, verbose_name='Can Access Change Requests'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='can_access_tasks',
            field=models.BooleanField(default=True, verbose_name='Can Access Tasks'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='can_access_reports',
            field=models.BooleanField(default=False, verbose_name='Can Access Reports'),
        ),
    ]