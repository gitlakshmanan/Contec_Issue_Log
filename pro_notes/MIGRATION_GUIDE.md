# Database Migration Guide - Professional Issue Management System

## Overview
This guide covers the migration from hardcoded choices to dynamic Foreign Key lookup tables for:
- **Customer** (formerly hardcoded CUSTOMERS)
- **IssueCategory** (formerly hardcoded ISSUE_CATEGORIES)
- **ImpactCategory** (formerly hardcoded IMPACT_CATEGORIES)

## Key Changes

### 1. Database Schema Changes
- `Issue.customer`: Changed from CharField with choices → ForeignKey to Customer model
- `Issue.issue_cat`: Changed from CharField with choices → ForeignKey to IssueCategory model
- `Issue.impact_category`: Changed from CharField with choices → ForeignKey to ImpactCategory model
- `Issue.impacted_customer`: Changed from CharField with dropdown → TextField for free text input

### 2. New Lookup Tables
Each lookup table includes:
- `name`: Unique name of the entry
- `code`: Optional unique code for reference
- `description`: Detailed description
- `is_active`: Boolean flag to enable/disable entries
- `created_at` / `updated_at`: Automatic timestamps

### 3. Benefits
✅ **Dynamic Management**: Add/edit customers and categories via Django Admin without code changes
✅ **Data Integrity**: Foreign key constraints ensure referential integrity
✅ **Audit Trail**: Track when entries were created/modified
✅ **Soft Delete**: Use `is_active` flag instead of deleting records
✅ **Professional UI**: AG Grid integration with advanced filtering, sorting, and export

## Migration Steps

### Step 1: Backup Your Database
```bash
# For SQLite
cp db.sqlite3 db.sqlite3.backup

# For PostgreSQL
pg_dump your_database > backup.sql

# For MySQL
mysqldump -u username -p database_name > backup.sql
```

### Step 2: Create Migrations
```bash
python manage.py makemigrations base
```

This will create a migration file that:
1. Creates new Customer, IssueCategory, and ImpactCategory tables
2. Adds temporary nullable fields to Issue model
3. Migrates existing data
4. Removes old fields and makes new fields required

### Step 3: Review Migration File
Check the generated migration file in `base/migrations/` and ensure it includes:
- Creation of lookup tables
- Data migration logic
- Field alterations on Issue model

### Step 4: Run Migrations
```bash
python manage.py migrate base
```

### Step 5: Seed Initial Data
```bash
python manage.py seed_lookup_tables
```

This will populate:
- **Customers**: Mediacom, Midco, Frontier
- **Issue Categories**: Man Error, Machine Error, Material Error, Method Error, Measurement Error
- **Impact Categories**: Undercharge, Overcharge, Credit, Debit

### Step 6: Verify Data
```bash
python manage.py shell
```

```python
from base.models import Customer, IssueCategory, ImpactCategory, Issue

# Check lookup tables
print(f"Customers: {Customer.objects.count()}")
print(f"Issue Categories: {IssueCategory.objects.count()}")
print(f"Impact Categories: {ImpactCategory.objects.count()}")

# Check issues are properly linked
print(f"Total Issues: {Issue.objects.count()}")
print(f"Issues with customer: {Issue.objects.exclude(customer=None).count()}")
```

### Step 7: Test the Application
1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Access the application at `http://localhost:8000`

3. Test key functionality:
   - View issues list (AG Grid interface)
   - Create new issue (dropdown for Customer, Issue Category, Impact Category)
   - Edit existing issue
   - Filter and sort in AG Grid
   - Export to CSV

### Step 8: Access Admin Interface
1. Navigate to `http://localhost:8000/admin`
2. Login with superuser credentials
3. Manage lookup tables:
   - **Customers**: Add new customers, edit existing ones
   - **Issue Categories**: Manage 5M categories
   - **Impact Categories**: Manage financial impact types

## Manual Data Migration (If Needed)

If you have existing issues and the automatic migration doesn't work perfectly:

```python
from base.models import Customer, IssueCategory, ImpactCategory, Issue

# Map old string values to new objects
customer_map = {
    'Mediacom': Customer.objects.get(name='Mediacom'),
    'Midco': Customer.objects.get(name='Midco'),
    'Frontier': Customer.objects.get(name='Frontier'),
}

category_map = {
    'ManError': IssueCategory.objects.get(name='Man Error'),
    'MachineError': IssueCategory.objects.get(name='Machine Error'),
    'MaterialError': IssueCategory.objects.get(name='Material Error'),
    'MethodError': IssueCategory.objects.get(name='Method Error'),
    'MeasureableError': IssueCategory.objects.get(name='Measurement Error'),
}

impact_map = {
    'Undercharge': ImpactCategory.objects.get(name='Undercharge'),
    'Overcharge': ImpactCategory.objects.get(name='Overcharge'),
    'Credit': ImpactCategory.objects.get(name='Credit'),
    'Debit': ImpactCategory.objects.get(name='Debit'),
}

# Update issues (if needed)
for issue in Issue.objects.all():
    # This is only needed if automatic migration failed
    pass
```

## Adding New Entries

### Via Django Admin (Recommended)
1. Go to Admin → Customers/Issue Categories/Impact Categories
2. Click "Add" button
3. Fill in the form:
   - **Name**: Display name (required, unique)
   - **Code**: Short code for reference (optional, unique)
   - **Description**: Detailed description (optional)
   - **Is Active**: Check to make it available (default: checked)
4. Save

### Via Django Shell
```python
from base.models import Customer

# Add new customer
Customer.objects.create(
    name='New Customer',
    code='NEW',
    description='Description of new customer',
    is_active=True
)
```

### Via Management Command
Create a custom management command for bulk imports.

## AG Grid Features

The new professional interface includes:

### Advanced Filtering
- **Text Filters**: Search in description, root cause, etc.
- **Set Filters**: Filter by customer, status, category
- **Number Filters**: Filter by revenue impact
- **Date Filters**: Filter by date ranges

### Sorting
- Click column headers to sort
- Multi-column sorting with Shift+Click
- Ascending/Descending toggle

### Column Management
- Resize columns by dragging
- Reorder columns by dragging headers
- Pin columns to left/right

### Export
- Export filtered/sorted data to CSV
- Maintains current view state

### Pagination
- 25 rows per page (default)
- Options: 10, 25, 50, 100 rows
- Client-side pagination for fast performance

## Troubleshooting

### Issue: Migration fails with "column already exists"
**Solution**: Drop the database and start fresh, or manually remove conflicting columns.

### Issue: Foreign key constraint error
**Solution**: Ensure all lookup tables are populated before creating issues.

### Issue: "Customer matching query does not exist"
**Solution**: Run `python manage.py seed_lookup_tables` to populate initial data.

### Issue: AG Grid not loading
**Solution**: Check browser console for JavaScript errors. Ensure CDN is accessible.

### Issue: Old issues not displaying
**Solution**: Check that foreign key relationships are properly set. Run data verification script.

## Rollback Plan

If you need to rollback:

1. Restore database backup:
   ```bash
   cp db.sqlite3.backup db.sqlite3
   ```

2. Revert code changes:
   ```bash
   git checkout HEAD~1 base/models.py base/forms.py base/views.py base/admin.py
   ```

3. Remove migration file:
   ```bash
   rm base/migrations/XXXX_add_lookup_tables.py
   ```

## Performance Considerations

- **select_related()**: Used in views to optimize database queries
- **Indexing**: Foreign keys are automatically indexed
- **Client-side operations**: AG Grid handles filtering/sorting on client side
- **Pagination**: Loads 1000 records max for AG Grid

## Security Notes

- Foreign key constraints prevent orphaned records
- `on_delete=models.PROTECT` prevents accidental deletion of referenced lookup entries
- Admin interface requires staff permissions
- All CRUD operations maintain audit trail

## Support

For issues or questions:
1. Check Django logs: `python manage.py runserver` output
2. Check browser console for JavaScript errors
3. Review migration files in `base/migrations/`
4. Test in Django shell for data integrity

## Next Steps

After successful migration:
1. ✅ Train users on new admin interface for managing lookup tables
2. ✅ Document process for adding new customers/categories
3. ✅ Set up regular database backups
4. ✅ Monitor performance with larger datasets
5. ✅ Consider adding more lookup tables (Invoice Types, Authorities, etc.)
