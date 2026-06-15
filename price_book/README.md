# Parts Price Manager Integration

## Overview
The Parts Price Manager application has been successfully integrated into your existing Django project (go_contec). This application manages part pricing with approval workflows and is optimized to handle 92,500+ records.

## What Was Done

### 1. Application Structure
- Created `price_book` app in the main project directory
- Integrated with existing authentication and user management
- Added dashboard metric card linking to Parts Price Manager

### 2. Database Optimizations for Large Datasets
The models include the following optimizations for handling 92,500 records:
- Database indexes on frequently queried fields (customer, partnumber, status, dates)
- Composite indexes for common query patterns
- select_related() and prefetch_related() in views to minimize database queries
- Pagination set to 50 records per page (adjustable)

### 3. Features
- Part price creation and management
- Multi-level approval workflow (Draft → Submitted → Reviewed → Approved)
- Customer, PO Number, and SO Number management
- Search and filter capabilities
- Activity logging for audit trail
- AJAX endpoints for dynamic data loading

### 4. Dashboard Integration
- Added "Parts Price Manager" metric card on the main dashboard
- Shows count of approved parts
- Clickable card that navigates to the parts list

## Setup Instructions

### Step 1: Run Migrations
```bash
cd c:\_2026_WORKSPACE\go_contec
python manage.py makemigrations price_book
python manage.py migrate
```

### Step 2: Create User Groups (Optional)
If you want to use the approval workflow, create these groups in Django admin:
```bash
python manage.py shell
```

Then in the Python shell:
```python
from django.contrib.auth.models import Group

# Create Reviewers group
reviewers = Group.objects.create(name='Reviewers')

# Create Approvers group
approvers = Group.objects.create(name='Approvers')

print("Groups created successfully!")
exit()
```

### Step 3: Access the Application
- Main Parts List: http://localhost:8000/parts/
- Create New Part: http://localhost:8000/parts/create/
- Dashboard: http://localhost:8000/dashboard/

### Step 4: Import Your 92,500 Records
You can import your data using Django's bulk_create for optimal performance:

```python
python manage.py shell
```

```python
from price_book.models import Customer, PartPrice
from django.contrib.auth.models import User
import csv
from datetime import datetime

# Get or create a user for created_by field
user = User.objects.first()  # or specify a specific user

# Example bulk import (adjust based on your CSV structure)
parts_to_create = []

with open('your_data.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Get or create customer
        customer, _ = Customer.objects.get_or_create(name=row['customer_name'])
        
        # Create part price object (don't save yet)
        part = PartPrice(
            customer=customer,
            partnumber=row['part_number'],
            price=row['price'],
            startdate=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
            margin=row.get('margin', 0),
            created_by=user,
            status='approved',  # Set to approved for existing data
            is_active=True
        )
        parts_to_create.append(part)
        
        # Bulk create every 1000 records for memory efficiency
        if len(parts_to_create) >= 1000:
            PartPrice.objects.bulk_create(parts_to_create, ignore_conflicts=True)
            parts_to_create = []
            print(f"Imported {len(parts_to_create)} records...")

# Import remaining records
if parts_to_create:
    PartPrice.objects.bulk_create(parts_to_create, ignore_conflicts=True)
    print(f"Import complete!")
```

## URL Structure

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

## Database Schema

### Customer
- name (unique)
- created_at

### PONumber
- po_number (unique)
- created_at

### SONumber
- so_number (unique)
- created_at

### PartPrice
- customer (FK)
- partnumber
- price
- startdate
- enddate (optional)
- margin
- po_number (FK, optional)
- so_number (FK, optional)
- created_by (FK to User)
- status (draft/submitted/reviewed/approved/rejected)
- reviewer (FK to User, optional)
- approver (FK to User, optional)
- remarks
- is_active
- Timestamps: created_date, updated_date, reviewer_date, approver_date

### ApprovalLog
- part_price (FK)
- user (FK)
- action
- comments
- created_date

## Performance Considerations

For 92,500 records:
1. Database indexes are already configured
2. Pagination is set to 50 records per page
3. Use select_related() for foreign key queries
4. Consider adding database connection pooling in production
5. Enable query caching if using PostgreSQL or MySQL

## Customization

### Adjust Pagination
Edit `price_book/views.py`, line ~25:
```python
paginator = Paginator(parts, 50)  # Change 50 to your preferred number
```

### Modify Status Choices
Edit `price_book/models.py`, PartPrice model:
```python
STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted for Review'),
    # Add more statuses as needed
]
```

## Troubleshooting

### Issue: Slow queries with large dataset
Solution: Ensure migrations have been run to create indexes
```bash
python manage.py sqlmigrate price_book 0001
```

### Issue: Memory errors during bulk import
Solution: Reduce batch size in bulk_create from 1000 to 500 or 250

### Issue: Dashboard card not showing
Solution: Ensure migrations are run and at least one part exists in the database

## Next Steps

1. Run migrations
2. Create user groups (if using approval workflow)
3. Import your 92,500 records
4. Test the application with sample data
5. Configure user permissions as needed

## Support

For issues or questions, refer to:
- Django documentation: https://docs.djangoproject.com/
- Project models: `price_book/models.py`
- Project views: `price_book/views.py`
