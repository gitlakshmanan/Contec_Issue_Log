import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from base.views import dashboard

print("=" * 60)
print("Dashboard Link Diagnostic")
print("=" * 60)

# Create a test request
factory = RequestFactory()
request = factory.get('/dashboard/')
request.user = User.objects.first()

# Add required attributes for messages framework
from django.contrib.messages.storage.fallback import FallbackStorage
setattr(request, 'session', {})
setattr(request, '_messages', FallbackStorage(request))

# Call the dashboard view
response = dashboard(request)

# Check if the response contains the parts link
content = response.content.decode('utf-8')

if 'href="/parts/"' in content:
    print("[OK] Parts link found in HTML: href=\"/parts/\"")
else:
    print("[ERROR] Parts link NOT found in HTML")
    
if 'Parts Price Manager' in content:
    print("[OK] 'Parts Price Manager' text found")
else:
    print("[ERROR] 'Parts Price Manager' text NOT found")

if 'cursor: pointer' in content:
    print("[OK] Cursor style found")
else:
    print("[ERROR] Cursor style NOT found")

print("\n" + "=" * 60)
print("SOLUTION:")
print("=" * 60)
print("1. Stop your Django server (Ctrl+C)")
print("2. Clear browser cache (Ctrl+Shift+Delete)")
print("3. Restart server: python manage.py runserver")
print("4. Hard refresh dashboard: Ctrl+F5")
print("=" * 60)
