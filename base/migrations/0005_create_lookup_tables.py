# Generated migration for lookup tables

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_issue_closed_at_alter_issue_id_alter_task_id_and_more'),
    ]

    operations = [
        # Step 1: Create lookup tables
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Customer Name')),
                ('code', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Customer Code')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='IssueCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Category Name')),
                ('code', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Category Code')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Issue Category',
                'verbose_name_plural': 'Issue Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ImpactCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Impact Category Name')),
                ('code', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='Impact Code')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Impact Category',
                'verbose_name_plural': 'Impact Categories',
                'ordering': ['name'],
            },
        ),
    ]
