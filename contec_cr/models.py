from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class ChangeRequest(models.Model):
    # CR Details
    effecting_app = models.CharField(max_length=100)
    cr_number = models.CharField(max_length=200, unique=True, blank=True, editable=False)
    cr_raised_by = models.CharField(max_length=100)
    cr_raised_on = models.DateField(default=timezone.now)
    cr_approved_by = models.CharField(max_length=100, blank=True, null=True)
    cr_approved_on = models.DateField(blank=True, null=True)
    cr_approved_by_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_change_requests',
        verbose_name='Approved By User'
    )
    
    # New fields
    department = models.CharField(max_length=100, blank=True, null=True)
    job_name = models.CharField(max_length=100, blank=True, null=True)
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('planned_medium', 'Planned-Medium'),
        ('planned_low', 'Planned-Low'),
        ('unplanned_high', 'Un-Planned-High'),
    ]
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Description
    description = models.TextField(blank=True)
    details_pre_cr = models.TextField(blank=True, null=True)
    details_post_cr = models.TextField(blank=True, null=True)
    back_up = models.CharField(max_length=100)
    
    # Deming's Cycle => PDCA (Plan-Do-Check-Act) Lakshmanan implements this in the following way:
    process_manager = models.CharField(max_length=100)
    resource_name = models.CharField(max_length=100)
    start_date = models.DateField(blank=True, null=True)
    identified_risks = models.TextField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    tested_on = models.DateField(blank=True, null=True)
    validated_on = models.DateField(blank=True, null=True)
    result_state = models.FileField(upload_to='attachments/', blank=True, null=True)
    
    # Justification
    change_benefits = models.TextField(blank=True, null=True)
    impacting_customer = models.CharField(max_length=100)
    remarks = models.CharField(max_length=500, blank=True, null=True)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # File attachment
    attachment = models.FileField(
        upload_to='cr_attachments/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Attachment',
        help_text='Upload documents (.pdf, .docx, .xlsx, .txt) up to 5MB'
    )
    
    def clean(self):
        """Validate that CR number cannot be modified if it exists"""
        if self.pk:
            original = ChangeRequest.objects.get(pk=self.pk)
            if original.cr_number and original.cr_number != self.cr_number:
                raise ValidationError({'cr_number': 'CR number cannot be modified once it has been assigned.'})
    
    def save(self, *args, **kwargs):
        # Generate CR number on first creation (not waiting for approval)
        # This allows multiple CR submissions without approval delays
        if not self.cr_number:
            # Get the current year
            current_year = timezone.now().year
            
            # Find the highest sequential number for this year
            year_prefix = f"CR-{current_year}-"
            last_cr = ChangeRequest.objects.filter(
                cr_number__startswith=year_prefix
            ).exclude(cr_number='').order_by('cr_number').last()
            
            new_number = 1
            if last_cr:
                try:
                    # Extract the last 4 digits from existing CR number
                    last_number = int(last_cr.cr_number.split('-')[-1])
                    new_number = last_number + 1
                except (ValueError, IndexError):
                    # Fallback to 1 if the previous CR number is malformed
                    new_number = 1
            
            self.cr_number = f"CR-{current_year}-{new_number:04d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.cr_number or f"CR-{self.id} (Draft)"