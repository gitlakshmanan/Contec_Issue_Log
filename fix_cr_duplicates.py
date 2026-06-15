"""
Script to fix duplicate cr_number issues in ChangeRequest model
Run this BEFORE the next CR creation to assign proper numbers to existing CRs
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
django.setup()

from contec_cr.models import ChangeRequest
from django.utils import timezone

def fix_duplicate_cr_numbers():
    """Fix any CRs with empty or duplicate cr_numbers"""
    
    print("=" * 60)
    print("FIXING DUPLICATE CR NUMBERS")
    print("=" * 60)
    
    # Find all CRs with empty cr_number
    empty_cr_crs = ChangeRequest.objects.filter(cr_number__in=['', None]).order_by('id')
    
    if not empty_cr_crs.exists():
        print("✓ No CRs with empty cr_number found. Database is clean!")
        return
    
    print(f"\nFound {empty_cr_crs.count()} CRs with empty cr_number")
    print("Assigning proper CR numbers...\n")
    
    current_year = timezone.now().year
    year_prefix = f"CR-{current_year}-"
    
    # Get the last CR number for this year
    last_cr = ChangeRequest.objects.filter(
        cr_number__startswith=year_prefix
    ).exclude(cr_number__in=['', None]).order_by('cr_number').last()
    
    next_number = 1
    if last_cr:
        try:
            last_number = int(last_cr.cr_number.split('-')[-1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    
    # Assign new CR numbers to all empty CRs
    for cr in empty_cr_crs:
        old_status = cr.status
        new_cr_number = f"CR-{current_year}-{next_number:04d}"
        cr.cr_number = new_cr_number
        cr.save()
        print(f"  ✓ CR #{cr.id:4d} (Status: {old_status:12s}) → {new_cr_number}")
        next_number += 1
    
    print(f"\n{'=' * 60}")
    print(f"✓ COMPLETE! Assigned {empty_cr_crs.count()} CR numbers")
    print(f"{'=' * 60}\n")

if __name__ == '__main__':
    try:
        fix_duplicate_cr_numbers()
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
