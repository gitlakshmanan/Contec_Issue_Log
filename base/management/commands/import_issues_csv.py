from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone
from base.models import Issue, Customer, IssueCategory, ImpactCategory
import csv
import os
from datetime import datetime


def parse_date(value):
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    # Try multiple common formats
    fmt_candidates = [
        '%m/%d/%Y', '%m/%d/%Y %H:%M', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ'
    ]
    for fmt in fmt_candidates:
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    # Last resort: try to parse just the date part
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


class Command(BaseCommand):
    help = 'Import issues from a CSV file. Optionally backup and delete existing issues first.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to CSV file to import (relative to project root or absolute)')
        parser.add_argument('--delete-existing', action='store_true', help='Delete all existing Issue rows before importing')
        parser.add_argument('--backup', action='store_true', help='Create a CSV backup of existing issues before deleting')
        parser.add_argument('--created-by', type=str, help='Username to set as created_by for imported rows (defaults to first user)')
        parser.add_argument('--dry-run', action='store_true', help='Validate and show summary without creating records')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        delete_existing = options['delete_existing']
        do_backup = options['backup']
        created_by_username = options.get('created_by')
        dry_run = options.get('dry_run')

        if not os.path.isabs(csv_path):
            base_dir = os.getcwd()
            csv_path = os.path.join(base_dir, csv_path)

        if not os.path.exists(csv_path):
            raise CommandError(f'CSV file not found: {csv_path}')

        User = get_user_model()
        created_by = None
        if created_by_username:
            created_by = User.objects.filter(username=created_by_username).first()
            if not created_by:
                raise CommandError(f'User not found: {created_by_username}')
        else:
            created_by = User.objects.first()
            if not created_by:
                raise CommandError('No user found in database (needed for created_by). Create a user first or pass --created-by')

        # Backup existing issues if requested
        if do_backup:
            backup_dir = os.path.join(os.getcwd(), 'base', 'exports')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'issues_backup_{timestamp}.csv')
            self.stdout.write(f'Backing up existing issues to {backup_path} ...')
            with open(backup_path, 'w', newline='', encoding='utf-8') as bf:
                writer = csv.writer(bf)
                # header similar to export_to_csv (includes Location)
                writer.writerow([
                    'ID', 'Location', 'Department', 'Customer', 'Invoice Type', 'Issue Category', 'Description',
                    'Identified On', 'Identified By', 'Revenue Impact', 'Impact Category',
                    'Root Cause', 'Root Cause Owner', 'Customer Received', 'Impacted Customers',
                    'Containment Action', 'Corrective Action', 'Rebilled/Credited', 'Rebill/Credit Proof',
                    'Action Owner', 'Due Date', 'Status', 'Approved By', 'Remarks',
                    'Attachment', 'Created By', 'Created At', 'Updated At'
                ])
                for issue in Issue.objects.all():
                    writer.writerow([
                        issue.id,
                        issue.location or '',
                        issue.department or '',
                        issue.customer.name if issue.customer else '',
                        issue.inv_type,
                        issue.issue_cat.name if issue.issue_cat else '',
                        issue.description,
                        issue.identified_on.strftime('%Y-%m-%d %H:%M:%S') if issue.identified_on else '',
                        issue.identified_by or '',
                        str(issue.revenue_impact or ''),
                        issue.impact_category.name if issue.impact_category else '',
                        issue.root_cause or '',
                        issue.root_cause_owner or '',
                        issue.customer_received or '',
                        issue.impacted_customer or '',
                        issue.containment_action or '',
                        issue.corrective_action or '',
                        issue.rebilled_credited or '',
                        issue.rebill_proof or '',
                        issue.action_owner or '',
                        issue.due_date.strftime('%Y-%m-%d %H:%M:%S') if issue.due_date else '',
                        issue.status or '',
                        issue.approved or '',
                        issue.remarks or '',
                        issue.attachment.name if issue.attachment else '',
                        issue.created_by.username if issue.created_by else '',
                        issue.created_at.strftime('%Y-%m-%d %H:%M:%S') if issue.created_at else '',
                        issue.updated_at.strftime('%Y-%m-%d %H:%M:%S') if issue.updated_at else '',
                    ])
            self.stdout.write(self.style.SUCCESS('Backup completed'))

        if delete_existing:
            self.stdout.write('Deleting existing Issue rows...')
            if dry_run:
                self.stdout.write(self.style.WARNING('Dry-run: would delete existing issues but --dry-run provided.'))
            else:
                Issue.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Existing issues deleted.'))
                # Reset autoincrement sequence so new IDs start from 1
                try:
                    if connection.vendor == 'sqlite':
                        with connection.cursor() as cursor:
                            cursor.execute("DELETE FROM sqlite_sequence WHERE name=%s", ['base_issue'])
                        self.stdout.write(self.style.SUCCESS('SQLite sequence reset for base_issue.'))
                    # Optionally handle PostgreSQL/MySQL if needed in the future
                except Exception as seq_err:
                    # Non-fatal: continue import even if sequence reset fails
                    self.stdout.write(self.style.WARNING(f'Could not reset sequence: {seq_err}'))

        # Read CSV and import
        success_count = 0
        error_rows = []
        rows_to_create = []
        with open(csv_path, newline='', encoding='utf-8') as cf:
            reader = csv.DictReader(cf)
            for idx, row in enumerate(reader, start=1):
                try:
                    # Normalize keys (strip)
                    def g(k):
                        return row.get(k, '') if k in row else row.get(k.strip(), '')

                    # Common header names we accept
                    location = row.get('Location') or row.get('location') or row.get('location_name') or ''
                    department = row.get('Department') or row.get('department') or ''
                    customer_name = row.get('Customer') or row.get('customer') or ''
                    inv_type = row.get('Invoice Type') or row.get('inv_type') or row.get('inv_type'.lower()) or ''
                    issue_cat_name = row.get('Issue Category') or row.get('Issue Cat') or row.get('issue_cat') or ''
                    description = row.get('Description') or row.get('description') or ''
                    identified_on = parse_date(row.get('Identified On') or row.get('identified_on') or '')
                    identified_by = row.get('Identified By') or row.get('identified_by') or ''
                    revenue_impact = row.get('Revenue Impact') or row.get('revenue_impact') or ''
                    impact_category_name = row.get('Impact Category') or row.get('impact_category') or ''
                    root_cause = row.get('Root Cause') or row.get('root_cause') or ''
                    root_cause_owner = row.get('Root Cause Owner') or row.get('root_cause_owner') or ''
                    customer_received = row.get('Customer Received') or row.get('customer_received') or ''
                    impacted_customer = row.get('Impacted Customers') or row.get('Impacted Customer') or ''
                    containment_action = row.get('Containment Action') or ''
                    corrective_action = row.get('Corrective Action') or ''
                    rebilled_credited = row.get('Rebilled/Credited') or row.get('rebilled_credited') or ''
                    rebill_proof = row.get('Rebill/Credit Proof') or row.get('rebill_proof') or ''
                    action_owner = row.get('Action Owner') or row.get('action_owner') or ''
                    due_date = parse_date(row.get('Due Date') or row.get('due_date') or '')
                    status = row.get('Status') or row.get('status') or 'Open'
                    approved = row.get('Approved By') or row.get('approved') or ''
                    remarks = row.get('Remarks') or row.get('remarks') or ''

                    # Resolve or create foreign keys
                    customer = None
                    if customer_name:
                        customer, _ = Customer.objects.get_or_create(name=customer_name.strip(), defaults={'is_active': True})

                    issue_cat = None
                    if issue_cat_name:
                        issue_cat, _ = IssueCategory.objects.get_or_create(name=issue_cat_name.strip(), defaults={'is_active': True})

                    impact_category = None
                    if impact_category_name:
                        impact_category, _ = ImpactCategory.objects.get_or_create(name=impact_category_name.strip(), defaults={'is_active': True})

                    # Revenue parse
                    rev_val = None
                    if revenue_impact:
                        try:
                            rev_val = float(str(revenue_impact).replace('$', '').replace(',', '').strip())
                        except Exception:
                            rev_val = None

                    issue_data = dict(
                        customer=customer,
                        inv_type=inv_type or '',
                        issue_cat=issue_cat,
                        description=description or '',
                        identified_on=identified_on or timezone.now(),
                        identified_by=identified_by or created_by.username,
                        revenue_impact=rev_val or 0,
                        impact_category=impact_category,
                        root_cause=root_cause or '',
                        root_cause_owner=root_cause_owner or '',
                        customer_received=customer_received or 'No',
                        impacted_customer=impacted_customer or '',
                        containment_action=containment_action or '',
                        corrective_action=corrective_action or '',
                        rebilled_credited=rebilled_credited or 'No',
                        rebill_proof=rebill_proof or '',
                        department=department or '',
                        location=location or '',
                        action_owner=action_owner or '',
                        due_date=due_date or (timezone.now() + timezone.timedelta(days=7)),
                        status=status or 'Open',
                        approved=approved or '',
                        remarks=remarks or '',
                        created_by=created_by,
                        updated_by=None,
                    )

                    if dry_run:
                        rows_to_create.append(issue_data)
                        success_count += 1
                    else:
                        with transaction.atomic():
                            Issue.objects.create(**issue_data)
                        success_count += 1

                except Exception as e:
                    error_rows.append((idx, str(e)))

        self.stdout.write(self.style.SUCCESS(f'Processed rows: {success_count}'))
        if error_rows:
            self.stdout.write(self.style.ERROR('Errors:'))
            for r in error_rows:
                self.stdout.write(self.style.ERROR(f'Row {r[0]}: {r[1]}'))
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry-run completed. No records were created.'))
        else:
            self.stdout.write(self.style.SUCCESS('Import completed.'))
