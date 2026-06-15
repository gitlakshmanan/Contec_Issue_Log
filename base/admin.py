from django.contrib import admin
from django.utils.html import format_html
import csv
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_str
from django.urls import path, reverse
from django.contrib import messages
from django.core.mail import EmailMessage
from .models import Task, Issue, UserProfile, Customer, IssueCategory, ImpactCategory
from .models import EmailLog

# Register your models here.

# ==================== LOOKUP TABLE ADMINS ====================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin interface for Customer lookup table"""
    list_display = ['name', 'code', 'is_active', 'issue_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'code', 'is_active')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def issue_count(self, obj):
        """Display count of issues for this customer"""
        count = obj.issues.count()
        return format_html(
            '<span style="background: #667eea; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold;">{}</span>',
            count
        )
    issue_count.short_description = 'Issues'


@admin.register(IssueCategory)
class IssueCategoryAdmin(admin.ModelAdmin):
    """Admin interface for Issue Category lookup table"""
    list_display = ['name', 'code', 'is_active', 'issue_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'code', 'is_active')
        }),
        ('Description', {
            'fields': ('description',),
            'description': 'Describe this issue category (e.g., Man, Machine, Material, Method, Measurement)'
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def issue_count(self, obj):
        """Display count of issues for this category"""
        count = obj.issues.count()
        return format_html(
            '<span style="background: #38f9d7; color: #333; padding: 3px 10px; border-radius: 12px; font-weight: bold;">{}</span>',
            count
        )
    issue_count.short_description = 'Issues'


@admin.register(ImpactCategory)
class ImpactCategoryAdmin(admin.ModelAdmin):
    """Admin interface for Impact Category lookup table"""
    list_display = ['name', 'code', 'is_active', 'issue_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Impact Category Information', {
            'fields': ('name', 'code', 'is_active')
        }),
        ('Description', {
            'fields': ('description',),
            'description': 'Describe this impact category (e.g., Undercharge, Overcharge, Credit, Debit)'
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def issue_count(self, obj):
        """Display count of issues for this impact category"""
        count = obj.issues.count()
        return format_html(
            '<span style="background: #fa709a; color: white; padding: 3px 10px; border-radius: 12px; font-weight: bold;">{}</span>',
            count
        )
    issue_count.short_description = 'Issues'


# ==================== MAIN MODEL ADMINS ====================

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer', 'inv_type', 'issue_cat', 'status', 
        'revenue_impact', 'due_date', 'created_by', 'created_at'
    ]
    list_filter = [
        'customer', 'inv_type', 'issue_cat', 'status', 'impact_category',
        'created_at', 'due_date', 'created_by'
    ]
    search_fields = [
        'description', 'root_cause', 'identified_by', 'customer',
        'containment_action', 'corrective_action'
    ]
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'inv_type', 'issue_cat', 'status')
        }),
        ('Issue Details', {
            'fields': ('description', 'root_cause', 'root_cause_owner')
        }),
        ('Identification', {
            'fields': ('identified_on', 'identified_by', 'due_date')
        }),
        ('Financial Impact', {
            'fields': ('revenue_impact', 'impact_category')
        }),
        ('Customer Impact', {
            'fields': ('customer_received', 'impacted_customer')
        }),
        ('Actions', {
            'fields': ('containment_action', 'corrective_action', 'rebilled_credited', 'rebill_proof', 'action_owner', 'approved')
        }),
        ('Additional Information', {
            'fields': ('remarks',)
        }),
        ('System Information', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        else:  # Updating existing object
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by', 'updated_by')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'status', 'department', 'approved_by', 
        'approved_at', 'created_at'
    ]
    list_filter = [
        'status', 'department', 'created_at', 'approved_at', 'approved_by'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 
        'user__last_name', 'department', 'phone_number'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'department', 'phone_number')
        }),
        ('Approval Status', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'approved_by')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'complete', 'created']
    list_filter = ['complete', 'created', 'user']
    search_fields = ['title', 'description']
    ordering = ['-created']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'issue', 'to_email', 'status', 'sent_by', 'created_at']
    list_display_links = ['id', 'issue']
    list_filter = ['status', 'sent_by', 'created_at']
    search_fields = ['to_email', 'subject', 'message', 'sent_by__username']
    readonly_fields = ['created_at', 'error']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        """Admin action: export selected EmailLog rows as CSV file."""
        field_names = ['id', 'issue_id', 'sent_by', 'to_email', 'cc_email', 'subject', 'message', 'status', 'error', 'created_at']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=emaillogs.csv'
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.issue.id if obj.issue else '',
                obj.sent_by.username if obj.sent_by else '',
                smart_str(obj.to_email),
                smart_str(obj.cc_email),
                smart_str(obj.subject),
                smart_str(obj.message),
                obj.status,
                smart_str(obj.error),
                obj.created_at.isoformat() if obj.created_at else ''
            ])
        return response
    export_as_csv.short_description = "Export selected EmailLogs as CSV"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:emaillog_id>/resend/', self.admin_site.admin_view(self.resend_view), name='base_emaillog_resend'),
        ]
        return custom_urls + urls

    def resend_view(self, request, emaillog_id, *args, **kwargs):
        """Admin view to resend an EmailLog record and create a new EmailLog for the attempt."""
        try:
            obj = EmailLog.objects.get(pk=emaillog_id)
        except EmailLog.DoesNotExist:
            self.message_user(request, 'EmailLog not found.', level=messages.ERROR)
            return HttpResponseRedirect(reverse('admin:base_emaillog_changelist'))

        # Prepare message
        to_list = [obj.to_email] if obj.to_email else []
        cc_list = [obj.cc_email] if obj.cc_email else []
        subject = obj.subject or ''
        body = obj.message or ''

        try:
            email = EmailMessage(subject=subject, body=body, to=to_list, cc=cc_list)
            email.send()
            # record a new EmailLog for this resend
            EmailLog.objects.create(
                issue=obj.issue,
                sent_by=request.user if request.user.is_authenticated else None,
                to_email=obj.to_email,
                cc_email=obj.cc_email,
                subject=subject,
                message=body,
                status='sent'
            )
            self.message_user(request, 'Email resent successfully.', level=messages.SUCCESS)
        except Exception as e:
            EmailLog.objects.create(
                issue=obj.issue,
                sent_by=request.user if request.user.is_authenticated else None,
                to_email=obj.to_email,
                cc_email=obj.cc_email,
                subject=subject,
                message=body,
                status='failed',
                error=str(e)
            )
            self.message_user(request, f'Failed to resend email: {e}', level=messages.ERROR)

        return HttpResponseRedirect(reverse('admin:base_emaillog_change', args=[emaillog_id]))