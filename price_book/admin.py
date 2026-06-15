from django.contrib import admin
from .models import Customer, PONumber, SONumber, PartPrice, ApprovalLog


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(PONumber)
class PONumberAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'created_at']
    search_fields = ['po_number']


@admin.register(SONumber)
class SONumberAdmin(admin.ModelAdmin):
    list_display = ['so_number', 'created_at']
    search_fields = ['so_number']


@admin.register(PartPrice)
class PartPriceAdmin(admin.ModelAdmin):
    list_display = ['partnumber', 'customer', 'price', 'margin', 'status', 'startdate', 'is_active']
    list_filter = ['status', 'is_active', 'customer']
    search_fields = ['partnumber', 'customer__name']
    date_hierarchy = 'created_date'
    readonly_fields = ['created_date', 'updated_date', 'reviewer_date', 'approver_date']


@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ['part_price', 'user', 'action', 'created_date']
    list_filter = ['action', 'created_date']
    search_fields = ['part_price__partnumber', 'user__username']
    date_hierarchy = 'created_date'
