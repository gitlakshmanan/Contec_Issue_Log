from django.core.management.base import BaseCommand
from contec_cr.models import ChangeRequest
from django.utils import timezone

class Command(BaseCommand):
    help = 'Fix duplicate cr_number issues in ChangeRequest model'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('FIXING DUPLICATE CR NUMBERS'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Find all CRs with empty cr_number
        empty_cr_crs = ChangeRequest.objects.filter(cr_number__in=['', None]).order_by('id')
        
        if not empty_cr_crs.exists():
            self.stdout.write(self.style.SUCCESS('\n✓ No CRs with empty cr_number found. Database is clean!'))
            return
        
        self.stdout.write(f'\nFound {empty_cr_crs.count()} CRs with empty cr_number')
        self.stdout.write('Assigning proper CR numbers...\n')
        
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
            self.stdout.write(f"  ✓ CR #{cr.id:4d} (Status: {old_status:12s}) → {new_cr_number}")
            next_number += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS(f'✓ COMPLETE! Assigned {empty_cr_crs.count()} CR numbers'))
        self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))
