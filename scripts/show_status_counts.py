import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','todo_list.settings')
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

django.setup()
from base.models import Issue
from django.db.models import Count

qs = Issue.objects.values('status').annotate(c=Count('id'))
print('STATUS_COUNTS:')
for r in qs:
    print(f"{r['status']}: {r['c']}")

closed_ids = [i.id for i in Issue.objects.filter(status='Closed')[:20]]
print('\nSAMPLE_CLOSED_IDS:', closed_ids)
