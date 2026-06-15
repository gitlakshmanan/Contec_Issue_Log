### View the Sample Issues

After creating, view them at:
- **All Issues:** http://127.0.0.1:8000/issues/
- **Dashboard:** http://127.0.0.1:8000/dashboard/
- **Statistics:** http://127.0.0.1:8000/statistics/
- **Closed Issues:** http://127.0.0.1:8000/issues/closed/

### Create 5 Sample Issues (Default)

```bash
python manage.py create_sample_issues
```

### Create Custom Number of Issues

```bash
python manage.py create_sample_issues --count 10
```

This will create up to 8 different sample issues (that's all we have defined).

## What Gets Created

The command creates realistic issues with:

### Issue #1 - Billing Error (Closed)
- **Customer:** Mediacom
- **Type:** Fulfillment
- **Category:** Man Error
- **Impact:** $150 Overcharge
- **Status:** Closed
- **Description:** Incorrect billing amount - manual data entry error

### Issue #2 - Duplicate Invoices (Open)
- **Customer:** Midco
- **Type:** C&C
- **Category:** Machine Error
- **Impact:** $2,500 Overcharge
- **Status:** Open
- **Description:** Automated system generated duplicate invoices

### Issue #3 - Wrong Pricing (Open)
- **Customer:** Frontier
- **Type:** OME
- **Category:** Material Error
- **Impact:** $500 Undercharge
- **Status:** Open
- **Description:** Outdated pricing sheet used

### Issue #4 - Calculation Error (Closed)
- **Customer:** Mediacom
- **Type:** Fulfillment
- **Category:** Method Error
- **Impact:** $750 Credit
- **Status:** Closed
- **Description:** Incorrect calculation method used

### Issue #5 - Measurement Error (Open)
- **Customer:** Midco
- **Type:** C&C
- **Category:** Measurable Error
- **Impact:** $1,200 Debit
- **Status:** Open
- **Description:** Faulty meter reading equipment

### Issue #6 - Discount Not Applied (Dismissed)
- **Customer:** Frontier
- **Type:** OME
- **Category:** Man Error
- **Impact:** $300 Overcharge
- **Status:** Dismissed
- **Description:** Service discount not applied correctly

### Issue #7 - System Timeout (Open)
- **Customer:** Mediacom
- **Type:** Fulfillment
- **Category:** Machine Error
- **Impact:** $0 (No financial impact)
- **Status:** Open
- **Description:** System timeout during invoice processing

### Issue #8 - Tax Rate Error (Open)
- **Customer:** Midco
- **Type:** C&C
- **Category:** Material Error
- **Impact:** $450 Undercharge
- **Status:** Open
- **Description:** Incorrect tax rate applied

## Features of Sample Data

Each issue includes:
- ✅ Realistic descriptions
- ✅ Root cause analysis
- ✅ Containment actions
- ✅ Corrective actions
- ✅ Revenue impact amounts
- ✅ Assigned owners
- ✅ Approval status
- ✅ Remarks/notes
- ✅ Proper dates (spread over last 30 days)
- ✅ Mix of Open, Closed, and Dismissed statuses

## Clear All Issues (If Needed)

If you want to start fresh:

```bash
python manage.py shell
```

```python
from base.models import Issue
Issue.objects.all().delete()
print("All issues deleted!")
exit()
```

## Quick Start Guide

1. **Create sample issues:**
   ```bash
   python manage.py create_sample_issues
   ```

2. **View them:**
   - Go to http://127.0.0.1:8000/issues/

3. **Test the system:**
   - View issue details
   - Edit an issue
   - Create a new issue
   - Close an issue
   - Export to CSV
   - View statistics

## Example Output

When you run the command, you'll see:

```
Creating 5 sample issues...
✓ Created Issue #1: Mediacom - ManError (Closed)
✓ Created Issue #2: Midco - MachineError (Open)
✓ Created Issue #3: Frontier - MaterialError (Open)
✓ Created Issue #4: Mediacom - MethodError (Closed)
✓ Created Issue #5: Midco - MeasureableError (Open)

✅ Successfully created 5 sample issues!
View them at: http://127.0.0.1:8000/issues/
```

## Statistics You'll See

After creating sample issues, your dashboard will show:
- **Total Issues:** 5-8 (depending on count)
- **Open Issues:** ~4-5
- **Closed Issues:** ~1-2
- **Dismissed Issues:** ~1
- **Total Revenue Impact:** ~$5,850
- **Issues by Customer:** Mediacom (3), Midco (3), Frontier (2)
- **Issues by Category:** Various distribution

## Notes

- All issues are created with the first available user (preferably superuser)
- Dates are spread over the last 30 days for realistic timeline
- Revenue impacts range from $0 to $2,500
- Mix of all issue categories (Man, Machine, Material, Method, Measurable)
- Mix of all impact categories (Overcharge, Undercharge, Credit, Debit)
- Realistic root causes and corrective actions included
