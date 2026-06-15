from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import csv
import io
from django.http import HttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==================== LOOKUP TABLES (Foreign Key Models) ====================

class Customer(models.Model):
    """Customer lookup table for dynamic customer management"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Customer Name")
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Customer Code")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
    
    def __str__(self):
        return self.name


class IssueCategory(models.Model):
    """Issue Category lookup table (5M Framework)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Category Code")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Issue Category"
        verbose_name_plural = "Issue Categories"
    
    def __str__(self):
        return self.name


class ImpactCategory(models.Model):
    """Impact Category lookup table for financial impact classification"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Impact Category Name")
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Impact Code")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Impact Category"
        verbose_name_plural = "Impact Categories"
    
    def __str__(self):
        return self.name


# Legacy choice fields for backward compatibility
CUSTOMER_CHOICES = [
    ('Astound', 'Astound'),
    ('Breezeline', 'Breezeline'),
    ('Cableone', 'Cableone'),
    ('Frontier', 'Frontier'),
    ('Mediacom', 'Mediacom'),
    ('Midcontinent', 'Midcontinent'),
    ('Tivo', 'Tivo'),
    ('Roku', 'Roku'),
    ('Ziply', 'Ziply'),
]
INVOICE_TYPES = [
    ('Fulfillment', 'Fulfillment'),
    ('C&C', 'C&C'),
    ('OME', 'OME'),
]

STATUS_CHOICES = [
    ('Open', 'Open'),
    ('Closed', 'Closed'),
    ('Dismissed', 'Dismissed'),
]

AUTHORITY_CHOICES = [
    ('patrick', 'Patrick'),
    ('neha', 'Neha'),
    ('verle', 'Verle'),
    ('prabhu', 'Prabhu'),
]

USER_STATUS_CHOICES = [
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('suspended', 'Suspended'),
]


class UserProfile(models.Model):
    """Extended user profile with approval status"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    status = models.CharField(
        max_length=20,
        choices=USER_STATUS_CHOICES,
        default='pending',
        verbose_name="Approval Status"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_users',
        verbose_name="Approved By"
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Approved At")
    rejection_reason = models.TextField(null=True, blank=True, verbose_name="Rejection Reason")
    department = models.CharField(max_length=100, null=True, blank=True, verbose_name="Department")
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="Phone Number")
    notes = models.TextField(null=True, blank=True, verbose_name="Admin Notes")
    # Whether to show tips on the issue create page (per-user preference)
    show_tips = models.BooleanField(default=True, verbose_name="Show Tips on Issue Create")
    # Whether user can access CR approval screen
    can_access_approvals = models.BooleanField(default=False, verbose_name="Can Access CR Approvals")
    
    # Menu Access Permissions
    can_access_issues = models.BooleanField(default=True, verbose_name="Can Access Issues")
    can_access_parts = models.BooleanField(default=False, verbose_name="Can Access Parts Price Book")
    can_access_cr = models.BooleanField(default=False, verbose_name="Can Access Change Requests")
    can_access_tasks = models.BooleanField(default=True, verbose_name="Can Access Tasks")
    can_access_reports = models.BooleanField(default=False, verbose_name="Can Access Reports")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_rejected(self):
        return self.status == 'rejected'

    @property
    def is_suspended(self):
        return self.status == 'suspended'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Issue(models.Model):
    """Main Issue model with comprehensive fields for issue management"""
    
    # Core fields with ForeignKey relationships
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='issues',
        verbose_name="Customer",
        help_text="Select the customer associated with this issue"
    )
    
    inv_type = models.CharField(
        max_length=50, 
        choices=INVOICE_TYPES,
        verbose_name="Invoice Type"
    )
    
    issue_cat = models.ForeignKey(
        IssueCategory,
        on_delete=models.PROTECT,
        related_name='issues',
        verbose_name="Issue Category",
        help_text="Select the issue category (5M Framework)"
    )
    
    description = models.TextField(
        default="No content provided.",
        verbose_name="Description"
    )
    
    identified_on = models.DateTimeField(
        default=timezone.now,
        verbose_name="Identified On"
    )
    
    identified_by = models.CharField(
        max_length=75,
        verbose_name="Identified By"
    )
    
    revenue_impact = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name="Revenue Impact ($)"
    )
    
    impact_category = models.ForeignKey(
        ImpactCategory,
        on_delete=models.PROTECT,
        related_name='issues',
        null=True,
        blank=True,
        verbose_name="Impact Category",
        help_text="Select the financial impact category"
    )
    
    root_cause = models.CharField(
        max_length=200,
        verbose_name="Root Cause"
    )
    
    root_cause_owner = models.CharField(
        max_length=75,
        verbose_name="Root Cause Owner"
    )
    
    YES_NO = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    customer_received = models.CharField(
        max_length=3,
        choices=YES_NO,
        default='No',
        verbose_name="Customer Received",
        help_text="Whether the customer has received the invoice/notice (Yes/No)"
    )
    
    impacted_customer = models.TextField(
        blank=True,
        null=True,
        verbose_name="Impacted Customers",
        help_text="Enter impacted customer names (free text)"
    )
    
    containment_action = models.TextField(
        default="No content provided.",
        verbose_name="Containment Action"
    )
    
    corrective_action = models.TextField(
        default="No content provided.",
        verbose_name="Corrective Action"
    )
    
    rebilled_credited = models.CharField(
        max_length=3,
        choices=YES_NO,
        default='No',
        verbose_name="Rebilled/Credited",
        help_text="Indicates if this issue was rebilled or credited (Yes/No)"
    )

    # Department for the issue (e.g., Billing, Operations) - added per user request
    department = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Department",
        help_text="Department responsible for this issue"
    )

    # Optional location field to capture where the issue occurred
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Location",
        help_text="Physical or logical location related to the issue (e.g., Site A, Router-12, Billing Zone)"
    )

    rebill_proof = models.TextField(
        null=True,
        blank=True,
        verbose_name="Rebill/Credit Proof",
        help_text="Details or proof for rebill/credit (invoice #, transaction ref, notes)"
    )
    
    action_owner = models.CharField(
        max_length=75,
        null=True,
        blank=True,
        default=" ",
        verbose_name="Action Owner"
    )
    
    due_date = models.DateTimeField(
        verbose_name="Due Date"
    )
    
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Open',
        verbose_name="Status"
    )
    
    approved = models.CharField(
        max_length=50,
        choices=AUTHORITY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Approved By"
    )
    
    remarks = models.TextField(
        null=True,
        blank=True,
        verbose_name="Remarks"
    )
    
    # User and timestamps
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='issues_created',
        verbose_name="Created By"
    )
    
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issues_updated',
        verbose_name="Updated By"
    )
    
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Closed At")
    
    # File upload field for documents and images
    attachment = models.FileField(
        upload_to='issue_attachments/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Attachment",
        help_text="Upload documents (.pdf, .docx, .xlsx) or images (.jpg, .png, .gif)"
    )

    class Meta:
        ordering = ['-id']
        permissions = [
            ("can_view_issue", "Can view issue"),
            ("can_add_issue", "Can add issue"),
            ("can_change_issue", "Can change issue"),
            ("can_delete_issue", "Can delete issue"),
            ("can_export_issue", "Can export issue"),
            ("can_import_issue", "Can import issue"),
        ]

    def __str__(self):
        return f"Issue #{self.id} - {self.customer.name if self.customer else 'N/A'} - {self.issue_cat.name if self.issue_cat else 'N/A'}"

    def clean(self):
        """Custom validation"""
        # Validate identified_on is not in the future
        if self.identified_on:
            today = timezone.now().date()
            identified_date = self.identified_on.date() if hasattr(self.identified_on, 'date') else self.identified_on
            if identified_date > today:
                raise ValidationError("Identified On date cannot be in the future. It must be today or earlier.")
        
        # Validate due date is not before identified date
        if self.due_date and self.identified_on:
            if self.due_date < self.identified_on:
                raise ValidationError("Due date cannot be before identified date")

    def save(self, *args, **kwargs):
        """Override save to handle status changes and set created_at"""
        # Set created_at to identified_on for new instances
        if not self.pk:
            self.created_at = self.identified_on
        
        # Check if status is being changed to 'Closed'
        if self.pk:
            try:
                old_instance = Issue.objects.get(pk=self.pk)
                if old_instance.status != 'Closed' and self.status == 'Closed':
                    from django.utils import timezone
                    self.closed_at = timezone.now()
                elif self.status != 'Closed':
                    self.closed_at = None
            except Issue.DoesNotExist:
                # New instance
                if self.status == 'Closed':
                    from django.utils import timezone
                    self.closed_at = timezone.now()
        else:
            # New instance
            if self.status == 'Closed':
                from django.utils import timezone
                self.closed_at = timezone.now()
        
        super().save(*args, **kwargs)

    @classmethod
    def export_to_csv(cls, queryset):
        """Export issues to CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header (include Department after ID)
        writer.writerow([
            'ID', 'Location', 'Department', 'Customer', 'Invoice Type', 'Issue Category', 'Description',
            'Identified On', 'Identified By', 'Revenue Impact', 'Impact Category',
            'Root Cause', 'Root Cause Owner', 'Customer Received', 'Impacted Customers',
            'Containment Action', 'Corrective Action', 'Rebilled/Credited', 'Rebill/Credit Proof',
            'Action Owner', 'Due Date', 'Status', 'Approved By', 'Remarks',
            'Attachment', 'Created By', 'Created At', 'Updated At'
        ])
        
        # Write data
        for issue in queryset:
            identified_on_str = issue.identified_on.strftime('%m/%d/%Y') if issue.identified_on else ''
            due_date_str = issue.due_date.strftime('%m/%d/%Y') if issue.due_date else ''
            writer.writerow([
                issue.id,
                issue.location or '',
                issue.department or '',
                issue.customer.name if issue.customer else '',
                issue.inv_type,
                issue.issue_cat.name if issue.issue_cat else '',
                issue.description, identified_on_str, issue.identified_by,
                issue.revenue_impact,
                issue.impact_category.name if issue.impact_category else '',
                issue.root_cause,
                issue.root_cause_owner, issue.customer_received or 'No', issue.impacted_customer or '',
                issue.containment_action, issue.corrective_action, issue.rebilled_credited or 'No',
                # include new rebill_proof field after rebilled_credited
                issue.rebill_proof or '',
                issue.action_owner, due_date_str, issue.status, issue.approved,
                issue.remarks, issue.attachment.name if issue.attachment else '',
                issue.created_by.username, issue.created_at, issue.updated_at
            ])
        
        return output.getvalue()


# Keep the old Task model for backward compatibility
class Task(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        order_with_respect_to = 'user'


class EmailLog(models.Model):
    """Audit trail for emails sent from the system related to issues"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='email_logs')
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    to_email = models.CharField(max_length=255)
    cc_email = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=[('sent', 'Sent'), ('failed', 'Failed')])
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"EmailLog(issue={self.issue_id}, to={self.to_email}, status={self.status})"


class Part(models.Model):
    """Parts price book model"""
    name = models.CharField(max_length=200, verbose_name="Part Name")
    part_number = models.CharField(max_length=100, unique=True, verbose_name="Part Number")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Price")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Part"
        verbose_name_plural = "Parts"

    def __str__(self):
        return f"{self.name} ({self.part_number})"
