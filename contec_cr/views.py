from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from contec_cr.models import ChangeRequest
from contec_cr.forms import ChangeRequestForm, ApprovalForm

def cr_list(request):
    return render(request, 'contec_cr/cr_list.html') 

@login_required
def cr_create(request):
    if request.method == 'POST':
        form = ChangeRequestForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Change Request created successfully.')
            return redirect('cr_list')
    else:
        form = ChangeRequestForm()
    return render(request, 'contec_cr/cr_form.html', {'form': form})

@login_required
def cr_edit(request, pk):
    cr = get_object_or_404(ChangeRequest, pk=pk)
    
    # Check if CR is approved - only the approving person can edit it
    if cr.status == 'approved':
        if not (request.user.is_superuser or 
                (cr.cr_approved_by_user and cr.cr_approved_by_user == request.user)):
            messages.error(request, 'Approved Change Requests can only be modified by the approving person or superuser.')
            return redirect('cr_detail', pk=cr.pk)
    
    if request.method == 'POST':
        form = ChangeRequestForm(request.POST, request.FILES, instance=cr)
        if form.is_valid():
            form.save()
            messages.success(request, 'Change Request updated successfully.')
            return redirect('cr_list')
    else:
        form = ChangeRequestForm(instance=cr)
    return render(request, 'contec_cr/cr_form.html', {'form': form, 'cr': cr})

def cr_detail(request, pk):
    cr = get_object_or_404(ChangeRequest, pk=pk)
    return render(request, 'contec_cr/cr_detail.html', {'cr': cr})

@login_required
def approval_screen(request):
    """Approval screen - only accessible to superusers or users with can_access_approvals permission"""
    # Check if user is superuser
    if not request.user.is_superuser:
        # Check if user has approval access granted by superuser
        try:
            profile = request.user.profile
            if not profile.can_access_approvals:
                messages.error(request, 'You do not have permission to access the approval screen.')
                return redirect('dashboard')
        except AttributeError:
            messages.error(request, 'You do not have permission to access the approval screen.')
            return redirect('dashboard')
    
    # Get CRs that are submitted but not approved
    pending_crs = ChangeRequest.objects.filter(status='submitted')
    return render(request, 'contec_cr/approval.html', {'pending_crs': pending_crs})

@login_required
def approve_cr(request, pk):
    """Approve a CR - only accessible to superusers or users with can_access_approvals permission"""
    # Check if user is superuser
    if not request.user.is_superuser:
        # Check if user has approval access granted by superuser
        try:
            profile = request.user.profile
            if not profile.can_access_approvals:
                messages.error(request, 'You do not have permission to approve CRs.')
                return redirect('dashboard')
        except AttributeError:
            messages.error(request, 'You do not have permission to approve CRs.')
            return redirect('dashboard')
    
    cr = get_object_or_404(ChangeRequest, pk=pk)
    if request.method == 'POST':
        form = ApprovalForm(request.POST, instance=cr)
        if form.is_valid():
            approved_cr = form.save(commit=False)
            # Track who approved this CR
            approved_cr.cr_approved_by_user = request.user
            approved_cr.save()
            status_msg = approved_cr.status.title()
            messages.success(request, f'CR {cr.cr_number or f"#{cr.pk}"} {status_msg} successfully.')
            return redirect('approval_screen')
    else:
        form = ApprovalForm(instance=cr)
    return render(request, 'contec_cr/approval_form.html', {'form': form, 'cr': cr})

# API endpoints for AJAX
@csrf_exempt
@require_http_methods(["GET"])
def get_cr_data(request):
    crs = ChangeRequest.objects.all().values(
        'id', 'cr_number', 'effecting_app', 'cr_raised_by',
        'cr_raised_on', 'status', 'process_manager', 'cr_approved_by'
    )
    return JsonResponse(list(crs), safe=False)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_cr(request, pk):
    cr = get_object_or_404(ChangeRequest, pk=pk)
    cr.delete()
    return JsonResponse({'status': 'success'})
