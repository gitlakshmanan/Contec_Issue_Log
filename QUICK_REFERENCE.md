# Parts Price Manager - Quick Reference Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Run Setup Script
```bash
cd c:\_2026_WORKSPACE\go_contec
setup_parts_manager.bat
```

### Step 2: Start Server
```bash
python manage.py runserver
```

### Step 3: Access Application
Open browser: http://localhost:8000/dashboard/
Click on "Parts Price Manager" card

---

## 📍 Access Points

### From Dashboard
- Click the **"Parts Price Manager"** metric card (4th card)
- Shows count of approved parts

### From Navigation Menu
- Click **"Parts Price"** dropdown in navbar
- Select "All Parts" or "New Part"

### Direct URLs
- All Parts: http://localhost:8000/parts/
- Create Part: http://localhost:8000/parts/create/
- Admin: http://localhost:8000/admin/

---

## 🔄 Workflow

```
1. CREATE (Draft)
   ↓
2. SUBMIT for Review
   ↓
3. REVIEW (Reviewers only)
   ↓
4. APPROVE (Approvers only)
   ↓
5. VISIBLE in Parts List
```

---

## 👥 User Roles

### Regular User
- Create parts (Draft status)
- Edit own draft parts
- Delete own draft parts
- View approved parts

### Reviewer (Group: "Reviewers")
- All Regular User permissions
- Review submitted parts
- Approve/Reject for next level

### Approver (Group: "Approvers")
- All Reviewer permissions
- Final approval of reviewed parts
- Approve/Reject parts

---

## 📊 Data Import (92,500 Records)

### Method 1: Django Shell (Recommended)
```python
python manage.py shell

from price_book.models import Customer, PartPrice
from django.contrib.auth.models import User
import csv
from datetime import datetime

user = User.objects.first()
parts_to_create = []

with open('your_data.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        customer, _ = Customer.objects.get_or_create(name=row['customer_name'])
        
        part = PartPrice(
            customer=customer,
            partnumber=row['part_number'],
            price=row['price'],
            startdate=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
            margin=row.get('margin', 0),
            created_by=user,
            status='approved',
            is_active=True
        )
        parts_to_create.append(part)
        
        if len(parts_to_create) >= 1000:
            PartPrice.objects.bulk_create(parts_to_create, ignore_conflicts=True)
            print(f"Imported {len(parts_to_create)} records...")
            parts_to_create = []

if parts_to_create:
    PartPrice.objects.bulk_create(parts_to_create, ignore_conflicts=True)
    print("Import complete!")
```

### Method 2: Django Admin
1. Go to http://localhost:8000/admin/
2. Navigate to "Part prices"
3. Use "Import" button (if django-import-export is installed)

---

## 🔍 Search & Filter

### Available Filters
- Part Number (text search)
- Customer (text search)
- Price range
- Date range
- Status

### Pagination
- Default: 50 records per page
- Adjustable in `views.py`

---

## 🗄️ Database Tables

| Table | Purpose | Records |
|-------|---------|---------|
| price_book_customer | Customer master | ~100 |
| price_book_ponumber | PO numbers | ~500 |
| price_book_sonumber | SO numbers | ~500 |
| price_book_partprice | **Main table** | **92,500** |
| price_book_approvallog | Audit trail | Variable |

---

## ⚡ Performance Tips

### For 92,500 Records:

1. **Use Indexes** (Already configured)
   - customer, partnumber, status, dates

2. **Pagination** (Already set to 50)
   - Adjust in `views.py` if needed

3. **Database Choice**
   - SQLite: OK for development
   - PostgreSQL/MySQL: Better for production

4. **Query Optimization**
   - Use select_related() (Already implemented)
   - Avoid N+1 queries

5. **Bulk Operations**
   - Use bulk_create() for imports
   - Process in batches of 1000

---

## 🎨 UI Components

### Dashboard Card
- Location: Main dashboard (4th card)
- Shows: Approved parts count
- Clickable: Yes → navigates to parts list

### Navigation Menu
- Location: Top navbar
- Menu: "Parts Price" dropdown
- Options: All Parts, New Part

### List View
- Pagination: 50 per page
- Search: Part number, customer
- Actions: View details

### Detail View
- Shows: All part information
- Activity log: Last 10 actions
- Actions: Edit (if draft), Delete (if draft)

---

## 🔧 Common Tasks

### Create User Groups
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import Group
Group.objects.create(name='Reviewers')
Group.objects.create(name='Approvers')
```

### Add User to Group
```python
from django.contrib.auth.models import User, Group
user = User.objects.get(username='john')
group = Group.objects.get(name='Reviewers')
user.groups.add(group)
```

### Check Part Count
```python
from price_book.models import PartPrice
print(f"Total parts: {PartPrice.objects.count()}")
print(f"Approved: {PartPrice.objects.filter(status='approved').count()}")
```

### Clear All Parts (Careful!)
```python
from price_book.models import PartPrice
PartPrice.objects.all().delete()
```

---

## 🐛 Troubleshooting

### Issue: Dashboard card shows 0
**Solution:** Import at least one part with status='approved'

### Issue: Slow queries
**Solution:** 
1. Check indexes: `python manage.py sqlmigrate price_book 0001`
2. Use PostgreSQL instead of SQLite
3. Reduce pagination size

### Issue: Can't access review/approval pages
**Solution:** Add user to appropriate group (Reviewers/Approvers)

### Issue: Import fails with memory error
**Solution:** Reduce batch size from 1000 to 500 or 250

### Issue: Navigation menu not showing
**Solution:** Clear browser cache and refresh

---

## 📁 File Structure

```
price_book/
├── models.py          # Database schema
├── views.py           # Business logic
├── urls.py            # URL routing
├── forms.py           # Form definitions
├── admin.py           # Admin interface
├── apps.py            # App configuration
├── README.md          # Detailed documentation
├── migrations/        # Database migrations
└── templates/
    └── price_book/
        ├── part_list.html
        ├── part_form.html
        ├── part_detail.html
        ├── review_list.html
        ├── approval_list.html
        └── ...
```

---

## 🔗 Useful Links

- Django Admin: http://localhost:8000/admin/
- Dashboard: http://localhost:8000/dashboard/
- Parts List: http://localhost:8000/parts/
- Create Part: http://localhost:8000/parts/create/
- Review Queue: http://localhost:8000/parts/review/
- Approval Queue: http://localhost:8000/parts/approval/

---

## 📞 Need Help?

1. Check `INTEGRATION_SUMMARY.md` for overview
2. Read `price_book/README.md` for detailed docs
3. Review `price_book/models.py` for database schema
4. Check `price_book/views.py` for business logic

---

## ✅ Checklist

- [ ] Run migrations: `python manage.py migrate`
- [ ] Create user groups (Reviewers, Approvers)
- [ ] Import sample data to test
- [ ] Verify dashboard card appears
- [ ] Test navigation menu
- [ ] Import full 92,500 records
- [ ] Test search and pagination
- [ ] Assign users to groups
- [ ] Test approval workflow

---

**Last Updated:** 2025
**Version:** 1.0
**Status:** Production Ready ✅
