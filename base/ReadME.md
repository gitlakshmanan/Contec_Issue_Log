
# go_contec Project

A Django-based issue tracking and parts price management system.

---

## Modules

### 1. Parts Price Manager (`price_book`)

#### Overview
Manages part pricing with approval workflows, optimized to handle **92,500+ records**.

#### Features
- Part price creation and management
- Multi-level approval workflow: **Draft → Submitted → Reviewed → Approved**
- Customer, PO Number, and SO Number management
- Search and filter capabilities
- Activity logging for audit trail
- AJAX endpoints for dynamic data loading
- Dashboard metric card showing count of approved parts

#### Database Optimizations
- Indexes on frequently queried fields (customer, partnumber, status, dates)
- Composite indexes for common query patterns
- `select_related()` and `prefetch_related()` to minimize DB queries
- Pagination set to 50 records per page

#### Setup Instructions

```bash
# Step 1: Run Migrations
python manage.py makemigrations price_book
python manage.py migrate
```

```python
# Step 2: Create User Groups (optional, for approval workflow)
from django.contrib.auth.models import Group
Group.objects.create(name='Reviewers')
Group.objects.create(name='Approvers')
```

#### Access the App
- Parts List: http://localhost:8000/parts/
- Create Part: http://localhost:8000/parts/create/
- Dashboard: http://localhost:8000/dashboard/

#### URL Structure

| URL | Description |
|-----|-------------|
| `/parts/` | List all approved parts |
| `/parts/create/` | Create new part price |
| `/parts/<id>/edit/` | Edit part price (draft only) |
| `/parts/<id>/delete/` | Delete part price (draft only) |
| `/parts/<id>/detail/` | View part details |
| `/parts/<id>/submit/` | Submit part for review |
| `/parts/review/` | Review submitted parts (Reviewers only) |
| `/parts/approval/` | Approve reviewed parts (Approvers only) |

#### Database Schema

**Customer**
- name (unique)
- created_at

**PONumber**
- po_number (unique)
- created_at

**SONumber**
- so_number (unique)
- created_at

**PartPrice**
- customer (FK)
- partnumber
- price
- startdate
- enddate (optional)
- margin
- po_number (FK, optional)
- so_number (FK, optional)
- created_by (FK to User)
- status (draft / submitted / reviewed / approved / rejected)
- reviewer (FK to User, optional)
- approver (FK to User, optional)
- remarks
- is_active
- Timestamps: created_date, updated_date, reviewer_date, approver_date

**ApprovalLog**
- part_price (FK)
- user (FK)
- action
- comments
- created_date

#### Bulk Import (92,500 Records)

```python
python manage.py shell
```

```python
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
            parts_to_create = []

if parts_to_create:
    PartPrice.objects.bulk_create(parts_to_create, ignore_conflicts=True)
    print("Import complete!")
```

#### Troubleshooting

| Issue | Solution |
|-------|----------|
| Slow queries with large dataset | Ensure migrations have been run to create indexes |
| Memory errors during bulk import | Reduce batch size in `bulk_create` from 1000 to 500 or 250 |
| Dashboard card not showing | Ensure migrations are run and at least one part exists in the database |

#### Customization

Adjust pagination in `price_book/views.py`:
```python
paginator = Paginator(parts, 50)  # Change 50 to your preferred number
```

Modify status choices in `price_book/models.py`:
```python
STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted for Review'),
    # Add more statuses as needed
]
```

---

### 2. To-Do List App (`pro_notes`)

A simple To-Do list app with User Registration, Login, Search, and full CRUD (Create, Read, Update, Delete) functionality.

---

## General Setup

### Requirements

```bash
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Run the Development Server

```bash
python manage.py runserver
```

### Run Migrations

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

---

## Performance Considerations (Large Datasets)

1. Database indexes are already configured
2. Pagination is set to 50 records per page
3. Use `select_related()` for foreign key queries
4. Consider adding database connection pooling in production
5. Enable query caching if using PostgreSQL or MySQL

---

## References

- Django Documentation: https://docs.djangoproject.com/
- Project models: `price_book/models.py`
- Project views: `price_book/views.py`
