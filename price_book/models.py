from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PONumber(models.Model):
    po_number = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['po_number']
    
    def __str__(self):
        return self.po_number


class SONumber(models.Model):
    so_number = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['so_number']
    
    def __str__(self):
        return self.so_number


class PartPrice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='part_prices')
    partnumber = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    startdate = models.DateField(db_index=True)
    enddate = models.DateField(null=True, blank=True)
    margin = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                 validators=[MinValueValidator(0), MaxValueValidator(100)])
    po_number = models.ForeignKey(PONumber, on_delete=models.SET_NULL, null=True, blank=True, related_name='part_prices')
    so_number = models.ForeignKey(SONumber, on_delete=models.SET_NULL, null=True, blank=True, related_name='part_prices')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_parts')
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField(auto_now=True)
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reviewed_parts', null=True, blank=True)
    reviewer_date = models.DateTimeField(null=True, blank=True)
    approver = models.ForeignKey(User, on_delete=models.PROTECT, related_name='approved_parts', null=True, blank=True)
    approver_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['customer', 'partnumber', 'is_active']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['-created_date']),
            models.Index(fields=['startdate', 'enddate']),
        ]
    
    def __str__(self):
        return f"{self.partnumber} - {self.customer.name}"
    
    @property
    def is_current(self):
        """Check if this price is currently active based on dates"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.startdate <= today:
            if self.enddate is None or self.enddate >= today:
                return True
        return False
    
    def save(self, *args, **kwargs):
        if self.status == 'approved' and not self.approver_date:
            self.approver_date = timezone.now()
        elif self.status == 'reviewed' and not self.reviewer_date:
            self.reviewer_date = timezone.now()
        super().save(*args, **kwargs)


class ApprovalLog(models.Model):
    part_price = models.ForeignKey(PartPrice, on_delete=models.CASCADE, related_name='approval_logs')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=50)
    comments = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.action} on {self.part_price.partnumber}"
