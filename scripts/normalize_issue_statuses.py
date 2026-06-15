"""
Normalize Issue.status values in the database.

Run from project root (PowerShell):
    .\.venv\Scripts\python.exe scripts\normalize_issue_statuses.py --apply

Without --apply it will only print a preview (safe dry-run).

This script trims whitespace and maps common variants to canonical statuses.
"""
import os
import sys
import argparse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
import django
django.setup()

from base.models import Issue

CANONICAL_MAP = {
    'open': 'Open',
    'opened': 'Open',
    'o': 'Open',
    'closed': 'Closed',
    'c': 'Closed',
    'dismissed': 'Dismissed',
    'dismiss': 'Dismissed',
    'in progress': 'In Progress',
    'inprogress': 'In Progress',
    'ip': 'In Progress',
}


def canonical_from_raw(raw):
    if raw is None:
        return None
    s = raw.strip()
    if not s:
        return s
    key = s.lower()
    # Normalize common separators
    key = key.replace('\t', ' ').replace('\n', ' ').strip()
    # Map if known
    if key in CANONICAL_MAP:
        return CANONICAL_MAP[key]
    # Fallback: title-case the status (e.g. "closed " -> "Closed")
    return s.title()


def preview_and_apply(apply=False):
    issues = Issue.objects.all()
    changes = []
    for issue in issues:
        old = issue.status
        new = canonical_from_raw(old)
        if new is None:
            continue
        if old != new:
            changes.append((issue.id, old, new))

    print(f'Total issues: {issues.count()}')
    print(f'Pending changes: {len(changes)}')
    for iid, old, new in changes[:200]:
        print(iid, repr(old), '->', repr(new))

    if apply and changes:
        print('\nApplying changes...')
        for iid, old, new in changes:
            Issue.objects.filter(id=iid).update(status=new)
        print('Done. Updated', len(changes), 'rows.')
    elif not apply:
        print('\nDry-run only. Re-run with --apply to perform updates.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Normalize Issue.status values')
    parser.add_argument('--apply', action='store_true', help='Apply changes to DB')
    args = parser.parse_args()

    preview_and_apply(apply=args.apply)
