
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import PartPrice, Customer, PONumber, SONumber, ApprovalLog
from .forms import PartPriceForm, PartPriceReviewForm, SearchForm, CustomerForm, PONumberForm, SONumberForm
from django.core.paginator import Paginator
import json

def is_reviewer(user):
    return user.groups.filter(name='Reviewers').exists()

def is_approver(user):
    return user.groups.filter(name='Approvers').exists()

@login_required
def part_list(request):
    form = SearchForm(request.GET or None)
    parts = PartPrice.objects.filter(is_active=True, status='approved')
    
    if form.is_valid():
        partnumber = form.cleaned_data.get('partnumber')
        customer = form.cleaned_data.get('customer')
        
        if partnumber:
            parts = parts.filter(partnumber__icontains=partnumber)
        if customer:
            parts = parts.filter(customer__name__icontains=customer)
    
    # Add search bars for each column
    column_searches = {}
    for field in ['partnumber', 'customer__name', 'price', 'margin', 'po_number__po_number', 'so_number__so_number']:
        search_term = request.GET.get(f'search_{field}', '')
        if search_term:
            parts = parts.filter(**{f'{field}__icontains': search_term})
        column_searches[field] = search_term
    
    paginator = Paginator(parts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pricebook/part_list.html', {
        'page_obj': page_obj,
        'form': form,
        'column_searches': column_searches,
    })

@login_required
def part_create(request):
    if request.method == 'POST':
        form = PartPriceForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.created_by = request.user
            part.save()
            
            # Log the creation
            ApprovalLog.objects.create(
                part_price=part,
                user=request.user,
                action='created',
                comments='Part price created'
            )
            
            messages.success(request, 'Part price created successfully and submitted for review.')
            return redirect('part_list')
    else:
        form = PartPriceForm()
    
    return render(request, 'pricebook/part_form.html', {'form': form, 'title': 'Add New Part Price'})

@login_required
def part_update(request, pk):
    part = get_object_or_404(PartPrice, pk=pk, created_by=request.user, status='draft')
    
    if request.method == 'POST':
        form = PartPriceForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            
            ApprovalLog.objects.create(
                part_price=part,
                user=request.user,
                action='updated',
                comments='Part price updated'
            )
            
            messages.success(request, 'Part price updated successfully.')
            return redirect('part_list')
    else:
        form = PartPriceForm(instance=part)
    
    return render(request, 'pricebook/part_form.html', {'form': form, 'title': 'Edit Part Price'})

@login_required
def part_delete(request, pk):
    part = get_object_or_404(PartPrice, pk=pk, created_by=request.user, status='draft')
    if request.method == 'POST':
        part.is_active = False
        part.save()
        
        ApprovalLog.objects.create(
            part_price=part,
            user=request.user,
            action='deleted',
            comments='Part price deleted'
        )
        
        messages.success(request, 'Part price deleted successfully.')
        return redirect('part_list')
    
    return render(request, 'pricebook/part_confirm_delete.html', {'part': part})

@login_required
def part_submit_for_review(request, pk):
    part = get_object_or_404(PartPrice, pk=pk, created_by=request.user, status='draft')
    part.status = 'submitted'
    part.save()
    
    ApprovalLog.objects.create(
        part_price=part,
        user=request.user,
        action='submitted_for_review',
        comments='Submitted for review'
    )
    
    messages.success(request, 'Part price submitted for review.')
    return redirect('part_list')

@login_required
@user_passes_test(is_reviewer)
def review_list(request):
    parts = PartPrice.objects.filter(status='submitted', is_active=True)
    return render(request, 'pricebook/review_list.html', {'parts': parts})

@login_required
@user_passes_test(is_reviewer)
def review_part(request, pk):
    part = get_object_or_404(PartPrice, pk=pk, status='submitted', is_active=True)
    
    if request.method == 'POST':
        form = PartPriceReviewForm(request.POST, instance=part)
        comments = request.POST.get('comments', '')
        
        if form.is_valid():
            part = form.save(commit=False)
            part.reviewer = request.user
            part.reviewer_date = None  # Will be set on save
            part.save()
            
            action = 'reviewed_approved' if part.status == 'reviewed' else 'reviewed_rejected'
            ApprovalLog.objects.create(
                part_price=part,
                user=request.user,
                action=action,
                comments=comments
            )
            
            messages.success(request, f'Part price {part.get_status_display().lower()}.')
            return redirect('review_list')
    else:
        form = PartPriceReviewForm(instance=part)
    
    return render(request, 'pricebook/review_detail.html', {'part': part, 'form': form})

@login_required
@user_passes_test(is_approver)
def approval_list(request):
    parts = PartPrice.objects.filter(status='reviewed', is_active=True)
    return render(request, 'pricebook/approval_list.html', {'parts': parts})

@login_required
@user_passes_test(is_approver)
def approve_part(request, pk):
    part = get_object_or_404(PartPrice, pk=pk, status='reviewed', is_active=True)
    
    if request.method == 'POST':
        form = PartPriceReviewForm(request.POST, instance=part)
        comments = request.POST.get('comments', '')
        
        if form.is_valid():
            part = form.save(commit=False)
            part.approver = request.user
            part.approver_date = None  # Will be set on save
            part.save()
            
            action = 'approved' if part.status == 'approved' else 'rejected'
            ApprovalLog.objects.create(
                part_price=part,
                user=request.user,
                action=action,
                comments=comments
            )
            
            messages.success(request, f'Part price {part.get_status_display().lower()}.')
            return redirect('approval_list')
    else:
        form = PartPriceReviewForm(instance=part)
    
    return render(request, 'pricebook/approval_detail.html', {'part': part, 'form': form})

@login_required
def part_detail(request, pk):
    part = get_object_or_404(PartPrice, pk=pk, is_active=True)
    logs = part.approval_logs.all()[:10]
    return render(request, 'pricebook/part_detail.html', {'part': part, 'logs': logs})

@login_required
def get_part_details(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        part_id = request.GET.get('id')
        part = get_object_or_404(PartPrice, pk=part_id, is_active=True)
        
        data = {
            'id': part.id,
            'customer': part.customer.name,
            'partnumber': part.partnumber,
            'price': str(part.price),
            'startdate': part.startdate.strftime('%Y-%m-%d'),
            'enddate': part.enddate.strftime('%Y-%m-%d') if part.enddate else '',
            'margin': str(part.margin),
            'po_number': part.po_number.po_number if part.po_number else '',
            'so_number': part.so_number.so_number if part.so_number else '',
            'created_date': part.created_date.strftime('%Y-%m-%d %H:%M'),
            'remarks': part.remarks,
            'status': part.get_status_display(),
        }
        return JsonResponse(data)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def create_customer_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        name = request.POST.get('name')
        if name:
            customer, created = Customer.objects.get_or_create(name=name)
            return JsonResponse({'id': customer.id, 'name': customer.name})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def create_po_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        po_number = request.POST.get('po_number')
        if po_number:
            po, created = PONumber.objects.get_or_create(po_number=po_number)
            return JsonResponse({'id': po.id, 'po_number': po.po_number})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def create_so_ajax(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        so_number = request.POST.get('so_number')
        if so_number:
            so, created = SONumber.objects.get_or_create(so_number=so_number)
            return JsonResponse({'id': so.id, 'so_number': so.so_number})
    return JsonResponse({'error': 'Invalid request'}, status=400)