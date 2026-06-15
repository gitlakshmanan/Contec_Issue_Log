from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import PartPrice, Customer, PONumber, SONumber, ApprovalLog
from .forms import PartPriceForm, PartPriceReviewForm, SearchForm, CSVUploadForm
from django.core.paginator import Paginator
import csv
import io
from datetime import datetime


def is_reviewer(user):
    return user.groups.filter(name='Reviewers').exists()


def is_approver(user):
    return user.groups.filter(name='Approvers').exists()


@login_required
def part_list(request):
    form = SearchForm(request.GET or None)
    parts = PartPrice.objects.filter(is_active=True, status='approved').select_related('customer', 'po_number', 'so_number', 'created_by')
    
    if form.is_valid():
        partnumber = form.cleaned_data.get('partnumber')
        customer = form.cleaned_data.get('customer')
        
        if partnumber:
            parts = parts.filter(partnumber__icontains=partnumber)
        if customer:
            parts = parts.filter(customer__name__icontains=customer)
    
    paginator = Paginator(parts, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Count draft parts for user
    draft_count = PartPrice.objects.filter(created_by=request.user, status='draft', is_active=True).count()
    
    return render(request, 'price_book/part_list.html', {
        'page_obj': page_obj,
        'form': form,
        'draft_count': draft_count,
    })


@login_required
def my_drafts(request):
    parts = PartPrice.objects.filter(created_by=request.user, status='draft', is_active=True).select_related('customer', 'po_number', 'so_number')
    
    paginator = Paginator(parts, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'price_book/my_drafts.html', {
        'page_obj': page_obj,
    })


@login_required
def part_create(request):
    if request.method == 'POST':
        form = PartPriceForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.created_by = request.user
            part.save()
            
            ApprovalLog.objects.create(
                part_price=part,
                user=request.user,
                action='created',
                comments='Part price created'
            )
            
            messages.success(request, 'Part price created successfully.')
            return redirect('part_list')
    else:
        form = PartPriceForm()
    
    return render(request, 'price_book/part_form.html', {'form': form, 'title': 'Add New Part Price'})


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
    
    return render(request, 'price_book/part_form.html', {'form': form, 'title': 'Edit Part Price'})


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
    
    return render(request, 'price_book/part_confirm_delete.html', {'part': part})


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
    parts = PartPrice.objects.filter(status='submitted', is_active=True).select_related('customer', 'created_by')
    return render(request, 'price_book/review_list.html', {'parts': parts})


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
            part.reviewer_date = None
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
    
    return render(request, 'price_book/review_detail.html', {'part': part, 'form': form})


@login_required
@user_passes_test(is_approver)
def approval_list(request):
    parts = PartPrice.objects.filter(status='reviewed', is_active=True).select_related('customer', 'created_by', 'reviewer')
    return render(request, 'price_book/approval_list.html', {'parts': parts})


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
            part.approver_date = None
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
    
    return render(request, 'price_book/approval_detail.html', {'part': part, 'form': form})


@login_required
def part_detail(request, pk):
    part = get_object_or_404(PartPrice.objects.select_related('customer', 'po_number', 'so_number', 'created_by', 'reviewer', 'approver'), pk=pk, is_active=True)
    logs = part.approval_logs.select_related('user').all()[:10]
    
    # Get price history for this part number and customer
    price_history = PartPrice.objects.filter(
        customer=part.customer,
        partnumber=part.partnumber,
        is_active=True,
        status='approved'
    ).select_related('po_number', 'so_number', 'created_by').order_by('-startdate')
    
    return render(request, 'price_book/part_detail.html', {
        'part': part,
        'logs': logs,
        'price_history': price_history
    })


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


@login_required
def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                return render(request, 'price_book/upload_csv.html', {'form': form})
            
            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                created_count = 0
                error_count = 0
                errors = []
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Get or create customer
                        customer_name = row.get('customer', '').strip()
                        if not customer_name:
                            errors.append(f'Row {row_num}: Customer name is required')
                            error_count += 1
                            continue
                        
                        customer, _ = Customer.objects.get_or_create(name=customer_name)
                        
                        # Validate required fields
                        partnumber = row.get('partnumber', '').strip()
                        if not partnumber:
                            errors.append(f'Row {row_num}: Part number is required')
                            error_count += 1
                            continue
                        
                        price_str = row.get('price', '').strip()
                        if not price_str:
                            errors.append(f'Row {row_num}: Price is required')
                            error_count += 1
                            continue
                        
                        startdate_str = row.get('startdate', '').strip()
                        if not startdate_str:
                            errors.append(f'Row {row_num}: Start date is required')
                            error_count += 1
                            continue
                        
                        # Get or create PO and SO numbers if provided
                        po_number = None
                        so_number = None
                        
                        if row.get('po_number', '').strip():
                            po_number, _ = PONumber.objects.get_or_create(po_number=row['po_number'].strip())
                        
                        if row.get('so_number', '').strip():
                            so_number, _ = SONumber.objects.get_or_create(so_number=row['so_number'].strip())
                        
                        # Parse dates
                        try:
                            startdate = datetime.strptime(startdate_str, '%Y-%m-%d').date()
                        except ValueError:
                            errors.append(f'Row {row_num}: Invalid start date format. Use YYYY-MM-DD')
                            error_count += 1
                            continue
                        
                        enddate = None
                        if row.get('enddate', '').strip():
                            try:
                                enddate = datetime.strptime(row['enddate'].strip(), '%Y-%m-%d').date()
                            except ValueError:
                                errors.append(f'Row {row_num}: Invalid end date format. Use YYYY-MM-DD')
                                error_count += 1
                                continue
                        
                        # Parse price and margin
                        try:
                            price = float(price_str)
                        except ValueError:
                            errors.append(f'Row {row_num}: Invalid price format')
                            error_count += 1
                            continue
                        
                        margin = 0
                        if row.get('margin', '').strip():
                            try:
                                margin = float(row['margin'].strip())
                            except ValueError:
                                errors.append(f'Row {row_num}: Invalid margin format')
                                error_count += 1
                                continue
                        
                        # Create PartPrice
                        part_price = PartPrice.objects.create(
                            customer=customer,
                            partnumber=partnumber,
                            price=price,
                            startdate=startdate,
                            enddate=enddate,
                            margin=margin,
                            po_number=po_number,
                            so_number=so_number,
                            remarks=row.get('remarks', '').strip(),
                            created_by=request.user,
                            status='draft'
                        )
                        
                        ApprovalLog.objects.create(
                            part_price=part_price,
                            user=request.user,
                            action='created_via_csv',
                            comments=f'Created via CSV upload'
                        )
                        
                        created_count += 1
                        
                    except Exception as e:
                        errors.append(f'Row {row_num}: {str(e)}')
                        error_count += 1
                
                if created_count > 0:
                    messages.success(request, f'Successfully imported {created_count} part prices.')
                
                if error_count > 0:
                    error_msg = f'{error_count} rows had errors:\n' + '\n'.join(errors[:10])
                    if len(errors) > 10:
                        error_msg += f'\n... and {len(errors) - 10} more errors'
                    messages.warning(request, error_msg)
                
                return redirect('part_list')
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        form = CSVUploadForm()
    
    return render(request, 'price_book/upload_csv.html', {'form': form})
