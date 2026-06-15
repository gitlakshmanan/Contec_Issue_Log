import os
import django
import csv
from datetime import datetime

import sys
# Ensure project root is on sys.path when this script is run directly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from base.models import Issue, IssueCategory, Customer, ImpactCategory

CSV_PATH = r'D:\_koding\contec\base_issue.utf8.csv'
DEFAULT_CATEGORY_NAME = 'Uncategorized'


def parse_date(value):
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    fmt_candidates = [
        '%m/%d/%Y', '%m/%d/%Y %H:%M', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ'
    ]
    for fmt in fmt_candidates:
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def get_or_create_customer(name):
    if not name:
        return None
    name = name.strip()
    if not name:
        return None
    customer, _ = Customer.objects.get_or_create(name=name, defaults={'is_active': True})
    return customer


def main():
    User = get_user_model()
    created_by = User.objects.first()
    if not created_by:
        print('No user found in DB; cannot set created_by for imported rows. Aborting.')
        return

    default_cat, _ = IssueCategory.objects.get_or_create(name=DEFAULT_CATEGORY_NAME, defaults={'is_active': True})
    print(f'Using default IssueCategory: {default_cat.name} (id={default_cat.id})')

    created_count = 0
    error_rows = []

    if not os.path.exists(CSV_PATH):
        print('CSV not found at', CSV_PATH)
        return

    with open(CSV_PATH, newline='', encoding='utf-8') as cf:
        reader = csv.DictReader(cf)
        for idx, row in enumerate(reader, start=1):
            try:
                issue_cat_name = (row.get('Issue Category') or row.get('Issue Cat') or row.get('issue_cat') or '').strip()
                # Only process rows where issue_cat is empty
                if issue_cat_name:
                    continue

                # Parse fields similar to import_issues_csv
                location = row.get('Location') or row.get('location') or ''
                department = row.get('Department') or row.get('department') or ''
                customer_name = row.get('Customer') or row.get('customer') or ''
                inv_type = row.get('Invoice Type') or row.get('inv_type') or ''
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

                customer = get_or_create_customer(customer_name)

                impact_category = None
                if impact_category_name:
                    impact_category, _ = ImpactCategory.objects.get_or_create(name=impact_category_name.strip(), defaults={'is_active': True})

                rev_val = None
                if revenue_impact:
                    try:
                        rev_val = float(str(revenue_impact).replace('$', '').replace(',', '').strip())
                    except Exception:
                        rev_val = None

                issue_data = dict(
                    customer=customer,
                    inv_type=inv_type or '',
                    issue_cat=default_cat,
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

                with transaction.atomic():
                    Issue.objects.create(**issue_data)
                created_count += 1

            except Exception as e:
                error_rows.append((idx, str(e)))

    # Final counts
    total_issues = Issue.objects.count()
    print(f'Created rows with default category: {created_count}')
    print(f'Errors while creating rows: {len(error_rows)}')
    if error_rows:
        for r in error_rows[:20]:
            print('Row', r[0], 'Error:', r[1])
    print('Total Issue rows now:', total_issues)


if __name__ == '__main__':
    main()
