
from django.contrib import admin
from .models import Customer, PONumber, SONumber, PartPrice, ApprovalLog

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(PONumber)
class PONumberAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'created_at']
    search_fields = ['po_number']
    ordering = ['po_number']

@admin.register(SONumber)
class SONumberAdmin(admin.ModelAdmin):
    list_display = ['so_number', 'created_at']
    search_fields = ['so_number']
    ordering = ['so_number']

@admin.register(PartPrice)
class PartPriceAdmin(admin.ModelAdmin):
    list_display = ['partnumber', 'customer', 'price', 'margin', 'status', 'created_by', 'created_date']
    list_filter = ['status', 'customer', 'created_date']
    search_fields = ['partnumber', 'customer__name']
    readonly_fields = ['created_date', 'updated_date', 'reviewer_date', 'approver_date']
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'partnumber', 'price', 'margin')
        }),
        ('Dates', {
            'fields': ('startdate', 'enddate')
        }),
        ('References', {
            'fields': ('po_number', 'so_number')
        }),
        ('Status & Approval', {
            'fields': ('status', 'created_by', 'reviewer', 'reviewer_date', 'approver', 'approver_date')
        }),
        ('Additional Info', {
            'fields': ('remarks', 'created_date', 'updated_date', 'is_active')
        }),
    )

@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ['part_price', 'user', 'action', 'created_date']
    list_filter = ['action', 'created_date']
    search_fields = ['part_price__partnumber', 'user__username']
    readonly_fields = ['created_date']