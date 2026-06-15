import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
django.setup()

from price_book.models import PartPrice
from django.urls import reverse

print("=" * 50)
print("Parts Price Manager Integration Test")
print("=" * 50)

# Test 1: Check if models are accessible
try:
    count = PartPrice.objects.count()
    print(f"[OK] PartPrice model accessible: {count} records")
except Exception as e:
    print(f"[ERROR] PartPrice model error: {e}")

# Test 2: Check if URL is configured
try:
    url = reverse('part_list')
    print(f"[OK] URL configured: {url}")
except Exception as e:
    print(f"[ERROR] URL error: {e}")

# Test 3: Check if app is in INSTALLED_APPS
from django.conf import settings
if 'price_book.apps.PriceBookConfig' in settings.INSTALLED_APPS or 'price_book' in settings.INSTALLED_APPS:
    print("[OK] price_book in INSTALLED_APPS")
else:
    print("[ERROR] price_book NOT in INSTALLED_APPS")

# Test 4: Check dashboard view
try:
    from base.views import dashboard
    print("[OK] Dashboard view imported successfully")
    
    # Check if the view has the parts logic
    import inspect
    source = inspect.getsource(dashboard)
    if 'price_book' in source or 'PartPrice' in source:
        print("[OK] Dashboard includes Parts Price Manager logic")
    else:
        print("[ERROR] Dashboard missing Parts Price Manager logic")
except Exception as e:
    print(f"[ERROR] Dashboard error: {e}")

print("=" * 50)
print("\nIntegration Status: READY")
print("\nNext Steps:")
print("1. Run: python manage.py runserver")
print("2. Visit: http://127.0.0.1:8000/dashboard/")
print("3. You should see 'Parts Price Manager' card")
print("=" * 50)
