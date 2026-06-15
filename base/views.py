from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, AccessMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.utils import timezone
import csv
import io
import json
from datetime import datetime, timedelta, time
from django.db import transaction
import logging
import os

# Imports for Reordering Feature
from django.views import View
from django.shortcuts import redirect
from django.db import transaction

from .models import Task, Issue, UserProfile, Customer, IssueCategory, ImpactCategory, Part
from .models import EmailLog
from .forms import PositionForm, IssueForm, IssueSearchForm, EmailForm, CSVUploadForm, UserApprovalForm, UserProfileForm, UserSearchForm
from contec_cr.models import ChangeRequest


class LoginPermissionMixin(AccessMixin):
    """Custom mixin that combines login and permission requirements"""
    permission_required = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Check if user is approved (skip for superusers)
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    if profile.is_rejected:
                        return redirect('rejected-user')
                    else:
                        return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        
        if self.permission_required and not request.user.has_perm(self.permission_required):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView): # Modification carried by clakshanan
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        # After login, if user is not a superuser and not approved, send to pending-approval
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated and not user.is_superuser:
            try:
                if not user.profile.is_approved:
                    return reverse_lazy('pending-approval')
            except Exception:
                return reverse_lazy('pending-approval')
        return reverse_lazy('welcome')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('welcome')

    def get_success_url(self):
        # After registration/login, redirect unapproved users to pending-approval
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated and not user.is_superuser:
            try:
                if not user.profile.is_approved:
                    return reverse_lazy('pending-approval')
            except Exception:
                return reverse_lazy('pending-approval')
        return super().get_success_url()

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('welcome')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter tasks to current user and compute counts
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        user_tasks = context['tasks']
        context['total_tasks'] = user_tasks.count()
        context['completed_tasks'] = user_tasks.filter(complete=True).count()
        context['remaining_tasks'] = user_tasks.filter(complete=False).count()
        # Backwards-compatible alias used elsewhere
        context['count'] = context['total_tasks']

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))


# ==================== ISSUE MANAGEMENT VIEWS ====================

class IssueList(LoginRequiredMixin, ListView):
    """Comprehensive Issue List View with AG Grid integration"""
    model = Issue
    context_object_name = 'issues'
    template_name = 'base/issue_list_aggrid.html'
    paginate_by = 1000

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Start with all issues and apply filters based on GET params
        queryset = Issue.objects.select_related('customer', 'issue_cat', 'impact_category', 'created_by', 'updated_by').all()

        # Get search parameters
        search = self.request.GET.get('search')
        customer = self.request.GET.get('customer')
        inv_type = self.request.GET.get('inv_type')
        issue_cat = self.request.GET.get('issue_cat')
        department = self.request.GET.get('department')
        status = self.request.GET.get('status')
        impact_category = self.request.GET.get('impact_category')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        # Default to ID ascending for stable, sequential numbering
        sort_by = self.request.GET.get('sort_by', 'id')

        # Apply search: broad text search across ID, customer, category, and text fields
        if search:
            search_term = search.strip()
            if search_term:
                try:
                    pk_val = int(search_term)
                    queryset = queryset.filter(
                        Q(pk=pk_val) |
                        Q(description__icontains=search_term) |
                        Q(root_cause__icontains=search_term) |
                        Q(identified_by__icontains=search_term) |
                        Q(containment_action__icontains=search_term) |
                        Q(corrective_action__icontains=search_term) |
                        Q(remarks__icontains=search_term) |
                        Q(action_owner__icontains=search_term) |
                        Q(impacted_customer__icontains=search_term) |
                        Q(department__icontains=search_term) |
                        Q(location__icontains=search_term) |
                        Q(customer__name__icontains=search_term) |
                        Q(issue_cat__name__icontains=search_term)
                    )
                except ValueError:
                    queryset = queryset.filter(
                        Q(description__icontains=search_term) |
                        Q(root_cause__icontains=search_term) |
                        Q(identified_by__icontains=search_term) |
                        Q(containment_action__icontains=search_term) |
                        Q(corrective_action__icontains=search_term) |
                        Q(remarks__icontains=search_term) |
                        Q(action_owner__icontains=search_term) |
                        Q(impacted_customer__icontains=search_term) |
                        Q(department__icontains=search_term) |
                        Q(location__icontains=search_term) |
                        Q(customer__name__icontains=search_term) |
                        Q(issue_cat__name__icontains=search_term)
                    )

        if customer:
            try:
                queryset = queryset.filter(customer_id=int(customer))
            except (TypeError, ValueError):
                pass

        if inv_type:
            queryset = queryset.filter(inv_type=inv_type)

        if issue_cat:
            try:
                queryset = queryset.filter(issue_cat_id=int(issue_cat))
            except (TypeError, ValueError):
                pass

        if department:
            dept_val = department.strip()
            if dept_val:
                # use substring, case-insensitive matching for flexibility
                queryset = queryset.filter(department__icontains=dept_val)

        if status:
            queryset = queryset.filter(status__iexact=status)

        if impact_category:
            try:
                queryset = queryset.filter(impact_category_id=int(impact_category))
            except (TypeError, ValueError):
                pass

        # Helper to parse date strings in MM/DD/YYYY or ISO formats and return aware datetimes
        def parse_date_to_range(date_str):
            if not date_str:
                return None, None
            # Try MM/DD/YYYY
            try:
                dt = datetime.strptime(date_str, '%m/%d/%Y').date()
            except Exception:
                # Try ISO
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                except Exception:
                    return None, None
            start = timezone.make_aware(datetime.combine(dt, time.min))
            end = timezone.make_aware(datetime.combine(dt, time.max))
            return start, end

        if date_from:
            start, _ = parse_date_to_range(date_from)
            if start:
                queryset = queryset.filter(identified_on__gte=start)

        if date_to:
            _, end = parse_date_to_range(date_to)
            if end:
                queryset = queryset.filter(identified_on__lte=end)

        # Annotate related names to guarantee text is available in templates
        queryset = queryset.annotate(issue_cat_name=F('issue_cat__name'))

        # Apply sorting (allowlist to prevent invalid field injection and to
        # ensure FK sorts use human-readable names)
        sort_map = {
            'id': 'id',
            '-id': '-id',
            'created_at': 'created_at',
            '-created_at': '-created_at',
            'identified_on': 'identified_on',
            '-identified_on': '-identified_on',
            'due_date': 'due_date',
            '-due_date': '-due_date',
            'revenue_impact': 'revenue_impact',
            '-revenue_impact': '-revenue_impact',
            'status': 'status',
            '-status': '-status',
            'department': 'department',
            '-department': '-department',
            'location': 'location',
            '-location': '-location',
            'inv_type': 'inv_type',
            '-inv_type': '-inv_type',
            # Sort FK fields by name, not by FK integer ID
            'customer': 'customer__name',
            '-customer': '-customer__name',
            'issue_cat': 'issue_cat__name',
            '-issue_cat': '-issue_cat__name',
        }
        order_expr = sort_map.get(sort_by, 'id')
        # Secondary ordering by ID keeps results stable within same key
        queryset = queryset.order_by(order_expr, 'id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Search form with current GET params so filters retain selected values
        context['search_form'] = IssueSearchForm(self.request.GET)

        # Add customers for dropdown
        context['customers'] = Customer.objects.filter(is_active=True)
        # Add unique, non-empty departments for dropdown filter (alphabetized)
        context['departments'] = Issue.objects.exclude(department__isnull=True).exclude(department__exact='')\
            .values_list('department', flat=True).distinct().order_by('department')

        # Add statistics
        queryset = self.get_queryset()
        context['total_issues'] = queryset.count()
        # Use case-insensitive lookups so minor casing differences don't hide counts
        context['open_issues'] = queryset.filter(status__iexact='Open').count()
        context['closed_issues'] = queryset.filter(status__iexact='Closed').count()
        context['dismissed_issues'] = queryset.filter(status__iexact='Dismissed').count()

        # Revenue impact statistics
        revenue_stats = queryset.aggregate(
            total_revenue_impact=Sum('revenue_impact')
        )
        context['total_revenue_impact'] = revenue_stats.get('total_revenue_impact', 0) or 0

        # Note: ID display uses the primary key (1,2,3,...) for clarity

        return context


class ClosedIssuesList(LoginRequiredMixin, ListView):
    """View for displaying only closed issues"""
    model = Issue
    context_object_name = 'issues'
    template_name = 'base/closed_issues_list.html'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Use case-insensitive lookup to include rows with casing/whitespace variations
        queryset = Issue.objects.select_related('customer', 'issue_cat', 'impact_category').filter(status__iexact='Closed')

        # Get search parameters
        search = self.request.GET.get('search')
        customer = self.request.GET.get('customer')
        inv_type = self.request.GET.get('inv_type')
        issue_cat = self.request.GET.get('issue_cat')
        impact_category = self.request.GET.get('impact_category')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        sort_by = self.request.GET.get('sort_by', '-closed_at')

        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(root_cause__icontains=search) |
                Q(identified_by__icontains=search) |
                Q(containment_action__icontains=search) |
                Q(corrective_action__icontains=search)
            )

        if customer:
            try:
                queryset = queryset.filter(customer_id=int(customer))
            except (TypeError, ValueError):
                pass

        if inv_type:
            queryset = queryset.filter(inv_type=inv_type)

        if issue_cat:
            try:
                queryset = queryset.filter(issue_cat_id=int(issue_cat))
            except (TypeError, ValueError):
                pass

        if impact_category:
            try:
                queryset = queryset.filter(impact_category_id=int(impact_category))
            except (TypeError, ValueError):
                pass

        # Helper to parse date strings in MM/DD/YYYY or ISO formats and return aware datetimes
        def parse_date_to_range(date_str):
            if not date_str:
                return None, None
            # Try MM/DD/YYYY
            try:
                dt = datetime.strptime(date_str, '%m/%d/%Y').date()
            except Exception:
                # Try ISO
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                except Exception:
                    return None, None
            start = timezone.make_aware(datetime.combine(dt, time.min))
            end = timezone.make_aware(datetime.combine(dt, time.max))
            return start, end

        if date_from:
            start, _ = parse_date_to_range(date_from)
            if start:
                queryset = queryset.filter(closed_at__gte=start)

        if date_to:
            _, end = parse_date_to_range(date_to)
            if end:
                queryset = queryset.filter(closed_at__lte=end)

        # Annotate related names to guarantee text is available in templates
        queryset = queryset.annotate(issue_cat_name=F('issue_cat__name'))

        # Apply sorting
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add search form
        context['search_form'] = IssueSearchForm(self.request.GET)
        
        # Add statistics
        queryset = self.get_queryset()
        context['total_closed_issues'] = queryset.count()
        
        # Revenue impact statistics for closed issues
        revenue_stats = queryset.aggregate(
            total_revenue_impact=Sum('revenue_impact')
        )
        # Calculate average separately
        total_count = queryset.count()
        if total_count > 0 and revenue_stats.get('total_revenue_impact'):
            revenue_stats['avg_revenue_impact'] = revenue_stats['total_revenue_impact'] / total_count
        else:
            revenue_stats['avg_revenue_impact'] = 0
            revenue_stats['total_revenue_impact'] = revenue_stats.get('total_revenue_impact', 0)
        
        context.update(revenue_stats)
        
        # Customer statistics for closed issues
        context['customer_stats'] = queryset.values('customer__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return context


class IssueDetail(LoginRequiredMixin, DetailView):
    """Detailed view of an issue"""
    model = Issue
    context_object_name = 'issue'
    template_name = 'base/issue_detail.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.select_related('customer', 'issue_cat', 'impact_category', 'created_by', 'updated_by').get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issue = self.object
        now = timezone.now()
        
        # Calculate days since identified
        if issue.identified_on:
            days_since_identified = (now - issue.identified_on).days
        else:
            days_since_identified = 0
        
        # Calculate days until due (negative if overdue)
        if issue.due_date:
            days_until_due = (issue.due_date - now).days
        else:
            days_until_due = 0
        
        context['now'] = now
        context['days_since_identified'] = days_since_identified
        context['days_until_due'] = days_until_due
        
        return context


class IssueCreate(LoginRequiredMixin, CreateView):
    """Create new issue"""
    model = Issue
    form_class = IssueForm
    template_name = 'base/issue_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if user is approved (skip for superusers)
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    if profile.is_rejected:
                        messages.error(request, 'Your account has been rejected.')
                        return redirect('rejected-user')
                    else:
                        messages.warning(request, 'Your account is pending approval.')
                        return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                messages.warning(request, 'Your account is pending approval.')
                return redirect('pending-approval')
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            # Set the created_by field to current user
            form.instance.created_by = self.request.user
            
            # Save the form
            response = super().form_valid(form)
            
            messages.success(self.request, f'Issue #{self.object.id} created successfully!')
            return response
            
        except Exception as e:
            messages.error(self.request, f'Error creating issue: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        for field, errors in form.errors.items():
            field_label = form.fields[field].label if field in form.fields else field
            for error in errors:
                messages.error(self.request, f'{field_label}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('issue-detail', kwargs={'pk': self.object.pk})


class IssueUpdate(LoginRequiredMixin, UpdateView):
    """Update existing issue"""
    model = Issue
    form_class = IssueForm
    template_name = 'base/issue_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            form.instance.updated_by = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, f'Issue #{self.object.id} updated successfully!')
            return response
        except Exception as e:
            messages.error(self.request, f'Error updating issue: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('issue-detail', kwargs={'pk': self.object.pk})


class IssueDelete(LoginRequiredMixin, DeleteView):
    """Delete issue"""
    model = Issue
    context_object_name = 'issue'
    template_name = 'base/issue_confirm_delete.html'
    success_url = reverse_lazy('issues')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            try:
                profile = request.user.profile
                if not profile.is_approved:
                    return redirect('pending-approval')
            except UserProfile.DoesNotExist:
                return redirect('pending-approval')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Issue deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def export_issues_csv(request):
    """Export issues to CSV. Respects GET params: status, search, customer, issue_cat, etc."""
    issues = Issue.objects.select_related('customer', 'issue_cat', 'impact_category', 'created_by').all()

    # Filter by status when requested (e.g. status=Closed for closed-issues page)
    status_param = request.GET.get('status')
    if status_param:
        issues = issues.filter(status__iexact=status_param.strip())

    # Apply same filters as list view if any
    search = request.GET.get('search')
    if search:
        issues = issues.filter(
            Q(description__icontains=search) |
            Q(root_cause__icontains=search) |
            Q(identified_by__icontains=search)
        )
    customer = request.GET.get('customer')
    if customer:
        try:
            issues = issues.filter(customer_id=int(customer))
        except (TypeError, ValueError):
            pass
    issue_cat = request.GET.get('issue_cat')
    if issue_cat:
        try:
            issues = issues.filter(issue_cat_id=int(issue_cat))
        except (TypeError, ValueError):
            pass
    department = request.GET.get('department')
    if department and department.strip():
        issues = issues.filter(department__icontains=department.strip())

    # Generate CSV
    csv_content = Issue.export_to_csv(issues)

    filename = "issues_export"
    if status_param and status_param.strip().lower() == 'closed':
        filename = "closed_issues_export"
    filename = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def import_issues_csv(request):
    """Import issues from CSV

    Note: this view intentionally does inline authentication handling so AJAX
    requests receive JSON 401 on unauthenticated access instead of a 302 redirect
    to the login page (which would return HTML and break JS clients).
    """
    # Determine AJAX early
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    # Inline authentication guard: return JSON 401 for AJAX, otherwise redirect
    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    if request.method == 'POST':
        
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            # Basic validation
            if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
                error_msg = 'File too large. Maximum size is 5MB.'
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('import-issues')
            
            try:
                # If client provided a server_path, prefer reading the file from the server filesystem
                server_path = form.cleaned_data.get('server_path') if hasattr(form, 'cleaned_data') else request.POST.get('server_path')
                file_obj = None
                filename = getattr(csv_file, 'name', '') or ''

                if server_path:
                    # Resolve import directory from settings or default to BASE_DIR/imports
                    import_dir = getattr(settings, 'IMPORT_DIR', None) or os.path.join(getattr(settings, 'BASE_DIR', os.getcwd()), 'imports')
                    # Prevent path traversal by normalizing
                    safe_path = os.path.normpath(os.path.join(import_dir, server_path))
                    if not safe_path.startswith(os.path.abspath(import_dir)):
                        raise PermissionError('Invalid server_path')
                    if not os.path.exists(safe_path):
                        raise FileNotFoundError(f'Server file not found: {server_path}')
                    # Open file in binary mode for downstream parsers
                    file_obj = open(safe_path, 'rb')
                    filename = os.path.basename(safe_path)
                    lower = filename.lower()
                else:
                    filename = getattr(csv_file, 'name', '') or ''
                    lower = filename.lower()

                # Helper to skip header for iterator-like readers
                def _skip_header_iter(it):
                    it = iter(it)
                    try:
                        next(it)
                    except StopIteration:
                        return None
                    return it

                if lower.endswith('.xlsx') or lower.endswith('.xls'):
                    # Try using openpyxl if installed
                    try:
                        import openpyxl
                    except Exception:
                        raise RuntimeError('Excel import requires openpyxl to be installed on the server')

                    # Use file_obj if server_path provided, else use uploaded file
                    wb = openpyxl.load_workbook(file_obj or csv_file, read_only=True, data_only=True)
                    sheet = wb.active
                    # Convert sheet rows to lists of strings
                    def sheet_rows():
                        for row in sheet.iter_rows(values_only=True):
                            yield [str(c) if c is not None else '' for c in row]

                    row_iter = sheet_rows()
                    # Skip header row
                    try:
                        next(row_iter)
                    except StopIteration:
                        error_msg = 'Empty Excel file.'
                        if is_ajax:
                            return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
                        messages.error(request, error_msg)
                        return redirect('import-issues')
                    reader = row_iter
                else:
                    # Default to CSV parsing
                    data_bytes = None
                    if file_obj:
                        data_bytes = file_obj.read()
                    else:
                        data_bytes = csv_file.read()
                    decoded_file = data_bytes.decode('utf-8')
                    io_string = io.StringIO(decoded_file)
                    # Try to sniff dialect, fall back to excel
                    sample = io_string.read(4096)
                    io_string.seek(0)
                    try:
                        dialect = csv.Sniffer().sniff(sample)
                        io_string.seek(0)
                        reader = csv.reader(io_string, dialect)
                    except Exception:
                        io_string.seek(0)
                        reader = csv.reader(io_string)

                    # Skip header
                    try:
                        next(reader)
                    except StopIteration:
                        error_msg = 'Empty CSV file.'
                        if is_ajax:
                            return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
                        messages.error(request, error_msg)
                        return redirect('import-issues')
                
                imported_count = 0
                errors = []
                
                # Process rows
                with transaction.atomic():
                    for line_no, row in enumerate(reader, start=2):
                        if len(row) < 10:  # Minimum required columns
                            errors.append({'line': line_no, 'error': 'Not enough columns'})
                            continue
                        
                        try:
                            # Get or create customer
                            customer_name = row[2].strip() if len(row) > 2 and row[2] else 'Unknown'
                            customer, created = Customer.objects.get_or_create(
                                name=customer_name,
                                defaults={'is_active': True}
                            )
                            
                            # Get or create issue category
                            category_name = row[4].strip() if len(row) > 4 and row[4] else 'General'
                            issue_cat, created = IssueCategory.objects.get_or_create(
                                name=category_name,
                                defaults={'is_active': True}
                            )
                            
                            # Create issue with basic fields
                            Issue.objects.create(
                                customer=customer,
                                inv_type=row[3] if len(row) > 3 and row[3] else 'Fulfillment',
                                issue_cat=issue_cat,
                                description=row[5] if len(row) > 5 and row[5] else 'No description',
                                identified_by=row[7] if len(row) > 7 and row[7] else 'Unknown',
                                root_cause=row[10] if len(row) > 10 and row[10] else 'Unknown',
                                root_cause_owner=row[11] if len(row) > 11 and row[11] else 'Unknown',
                                created_by=request.user
                            )
                            imported_count += 1
                            
                        except Exception as e:
                            errors.append({'line': line_no, 'error': str(e)})
                            continue
                
                # Prepare summary
                summary = {
                    'imported_count': imported_count,
                    'errors': errors
                }
                
                # Return appropriate response
                if is_ajax:
                    return JsonResponse({'status': 'success', 'summary': summary})
                else:
                    # Show results for regular form submission
                    if imported_count > 0:
                        messages.success(request, f'Successfully imported {imported_count} issues!')
                    if errors:
                        for error in errors[:5]:  # Show first 5 errors
                            messages.warning(request, f"Line {error['line']}: {error['error']}")
                        if len(errors) > 5:
                            messages.warning(request, f'... and {len(errors) - 5} more errors')
                    return redirect('issues')
                
            except Exception as e:
                error_msg = f'Error processing CSV: {str(e)}'
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': error_msg}, status=500)
                messages.error(request, error_msg)
                return redirect('import-issues')
        else:
            # Form validation errors
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Invalid form data'}, status=400)
    
    else:
        form = CSVUploadForm()

    return render(request, 'base/import_csv.html', {'form': form})


@login_required
def download_template_csv(request):
    """Return a sample CSV template for imports."""
    # Construct a small CSV in memory matching the expected header
    header = [
        'ID', 'Department', 'Customer', 'Invoice Type', 'Issue Category', 'Description', 'Identified On',
        'Identified By', 'Revenue Impact', 'Impact Category', 'Root Cause', 'Root Cause Owner',
        'Customer Received', 'Impacted Customers', 'Containment Action', 'Corrective Action',
        'Rebilled/Credited', 'Rebill/Credit Proof', 'Action Owner', 'Due Date', 'Status', 'Approved By',
        'Remarks', 'Attachment', 'Created By', 'Created At', 'Updated At'
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    # Add an example row (values are optional; kept minimal)
    writer.writerow(['', 'Finance', 'Acme Corp', 'Standard', 'Billing', 'Example issue description', '2025-10-01',
                     'Alice', '1000', '', 'Incorrect calculation', 'Bob', 'No', '', 'Containment action',
                     'Corrective action', 'No', '', 'Bob', '2025-10-15', 'Open', '', '', '', '', '', ''])

    resp = HttpResponse(output.getvalue(), content_type='text/csv')
    resp['Content-Disposition'] = 'attachment; filename=issues_template.csv'
    return resp


@login_required
def send_email_popup(request, issue_id):
    """Handle email popup functionality"""
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            try:
                # Prepare email content
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']
                to_email = form.cleaned_data['to_email']
                cc_email = form.cleaned_data.get('cc_email')
                
                if form.cleaned_data.get('include_issue_details'):
                    # Include issue details in email
                    issue_details = f"""
Issue Details:
- Issue ID: {issue.id}
- Customer: {issue.customer}
- Invoice Type: {issue.inv_type}
- Issue Category: {issue.issue_cat}
- Description: {issue.description}
- Status: {issue.status}
- Due Date: {issue.due_date}
- Revenue Impact: ${issue.revenue_impact}
- Root Cause: {issue.root_cause}
- Action Owner: {issue.action_owner}

Original Message:
{message}
"""
                    message = issue_details
                
                # Send email
                email = EmailMessage(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [to_email],
                    cc=[cc_email] if cc_email else None,
                )
                
                email.send()
                # Record audit log
                try:
                    EmailLog.objects.create(
                        issue=issue,
                        sent_by=request.user if request.user.is_authenticated else None,
                        to_email=to_email,
                        cc_email=cc_email,
                        subject=subject,
                        message=message,
                        status='sent'
                    )
                except Exception:
                    # Don't block response if logging fails
                    pass

                messages.success(request, 'Email sent successfully!')
                return JsonResponse({'status': 'success', 'message': 'Email sent successfully!'})
                
            except Exception as e:
                # Log failure
                try:
                    EmailLog.objects.create(
                        issue=issue,
                        sent_by=request.user if request.user.is_authenticated else None,
                        to_email=form.data.get('to_email') or '',
                        cc_email=form.data.get('cc_email') or '',
                        subject=form.data.get('subject') or '',
                        message=form.data.get('message') or '',
                        status='failed',
                        error=str(e)
                    )
                except Exception:
                    pass

                messages.error(request, f'Error sending email: {str(e)}')
                return JsonResponse({'status': 'error', 'message': str(e)})
    
    else:
        # Pre-populate form with issue details
        initial_data = {
            'subject': f'Issue #{issue.id} - {issue.customer} - {issue.issue_cat}',
            'message': f'Hello,\n\nI would like to discuss Issue #{issue.id} regarding {issue.customer}.\n\nPlease find the details below:\n\n'
        }
        form = EmailForm(initial=initial_data)
    
    return render(request, 'base/email_popup.html', {
        'form': form,
        'issue': issue
    })


@login_required
def issue_statistics(request):
    """Display issue statistics and analytics with calendar year filtering"""
    # Check if user is approved
    if not request.user.is_superuser:
        try:
            profile = request.user.profile
            if not profile.is_approved:
                return redirect('pending-approval')
        except UserProfile.DoesNotExist:
            return redirect('pending-approval')
    
    # Get calendar year from request, default to current year
    current_year = timezone.now().year
    selected_year = int(request.GET.get('year', current_year))
    
    # Calendar year starts from January 1st to December 31st
    year_start = timezone.make_aware(datetime(selected_year, 1, 1))
    year_end = timezone.make_aware(datetime(selected_year, 12, 31, 23, 59, 59))
    
    # Filter issues by calendar year
    issues = Issue.objects.select_related('customer', 'issue_cat', 'impact_category').filter(
        created_at__gte=year_start,
        created_at__lte=year_end
    )
    
    # Basic statistics
    total_issues = issues.count()
    open_issues = issues.filter(status__iexact='Open').count()
    closed_issues = issues.filter(status__iexact='Closed').count()
    dismissed_issues = issues.filter(status__iexact='Dismissed').count()
    
    # Revenue statistics
    revenue_stats = issues.aggregate(
        total_revenue=Sum('revenue_impact')
    )
    if total_issues > 0 and revenue_stats.get('total_revenue'):
        revenue_stats['avg_revenue'] = revenue_stats['total_revenue'] / total_issues
    else:
        revenue_stats['avg_revenue'] = 0
        revenue_stats['total_revenue'] = revenue_stats.get('total_revenue', 0)
    
    # Customer breakdown
    customer_stats = issues.select_related('customer').values('customer__name').annotate(
        count=Count('id'),
        total_revenue=Sum('revenue_impact')
    ).order_by('-count')
    
    # Issue category breakdown
    category_stats = issues.select_related('issue_cat').values('issue_cat__name').annotate(
        count=Count('id')
    ).order_by('-count')

    # Department breakdown (exclude null/empty department values)
    department_stats = issues.exclude(department__isnull=True).exclude(department__exact='').values('department').annotate(
        count=Count('id'),
        total_revenue=Sum('revenue_impact')
    ).order_by('-count')

    # Location breakdown (exclude null/empty location values)
    location_stats = issues.exclude(location__isnull=True).exclude(location__exact='').values('location').annotate(
        count=Count('id'),
        total_revenue=Sum('revenue_impact')
    ).order_by('-count')
    
    # Monthly trends for selected calendar year (January to December)
    monthly_stats = []
    for month in range(1, 13):  # January (1) to December (12)
        month_start = timezone.make_aware(datetime(selected_year, month, 1))
        
        # Calculate month end
        if month == 12:
            month_end = timezone.make_aware(datetime(selected_year + 1, 1, 1)) - timedelta(seconds=1)
        else:
            month_end = timezone.make_aware(datetime(selected_year, month + 1, 1)) - timedelta(seconds=1)
        
        month_issues = issues.filter(created_at__gte=month_start, created_at__lte=month_end)
        
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%b %Y'),
            'count': month_issues.count(),
            'open': month_issues.filter(status__iexact='Open').count(),
            'closed': month_issues.filter(status__iexact='Closed').count(),
        })
    
    # Available years for dropdown (last 5 years)
    available_years = list(range(current_year - 4, current_year + 1))
    
    context = {
        'selected_year': selected_year,
        'available_years': available_years,
        'year_start': year_start,
        'year_end': year_end,
        'total_issues': total_issues,
        'open_issues': open_issues,
        'closed_issues': closed_issues,
        'dismissed_issues': dismissed_issues,
        'revenue_stats': revenue_stats,
        'customer_stats': customer_stats,
        'category_stats': category_stats,
        'department_stats': department_stats,
        'location_stats': location_stats,
        'monthly_stats': monthly_stats,
    }
    
    return render(request, 'base/issue_statistics.html', context)


@login_required
def dashboard(request):
    """Main dashboard view"""
    # Recent issues with related objects
    recent_issues = Issue.objects.select_related('customer', 'issue_cat', 'created_by').all()[:5]
    
    # Issues by status
    issues_by_status = Issue.objects.values('status').annotate(count=Count('id'))
    
    # Overdue issues with related objects
    overdue_issues = Issue.objects.select_related('customer', 'issue_cat').filter(
        due_date__lt=timezone.now(),
        status__iexact='Open'
    )[:5]
    
    # User's tasks
    user_tasks = Task.objects.filter(user=request.user)[:5]
    
    # Parts count from our Part model
    total_parts = Part.objects.filter(is_active=True).count()
    
    context = {
        'recent_issues': recent_issues,
        'issues_by_status': issues_by_status,
        'overdue_issues': overdue_issues,
        'user_tasks': user_tasks,
        'total_issues': Issue.objects.count(),
        'open_issues': Issue.objects.filter(status__iexact='Open').count(),
        'closed_issues': Issue.objects.filter(status__iexact='Closed').count(),
        'total_parts': total_parts,
        'now': timezone.now(),
    }
    
    return render(request, 'base/dashboard.html', context)


@login_required
def close_issue(request, issue_id):
    """Function to close an issue"""
    # Check if user is approved
    if not request.user.is_superuser:
        try:
            profile = request.user.profile
            if not profile.is_approved:
                return redirect('pending-approval')
        except UserProfile.DoesNotExist:
            return redirect('pending-approval')
    
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        issue.status = 'Closed'
        issue.closed_at = timezone.now()
        issue.updated_by = request.user
        issue.save()
        
        messages.success(request, f'Issue #{issue.id} has been closed successfully!')
        
        # Redirect back to the issue detail page or issues list
        if 'next' in request.GET:
            return redirect(request.GET['next'])
        else:
            return redirect('issue-detail', pk=issue.id)
    
    return render(request, 'base/close_issue_confirm.html', {'issue': issue})


@login_required
def reopen_issue(request, issue_id):
    """Function to reopen a closed issue"""
    # Check if user is approved
    if not request.user.is_superuser:
        try:
            profile = request.user.profile
            if not profile.is_approved:
                return redirect('pending-approval')
        except UserProfile.DoesNotExist:
            return redirect('pending-approval')
    
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        issue.status = 'Open'
        issue.closed_at = None
        issue.updated_by = request.user
        issue.save()
        
        messages.success(request, f'Issue #{issue.id} has been reopened successfully!')
        
        # Redirect back to the issue detail page or issues list
        if 'next' in request.GET:
            return redirect(request.GET['next'])
        else:
            return redirect('issue-detail', pk=issue.id)
    
    return render(request, 'base/reopen_issue_confirm.html', {'issue': issue})


# ==================== USER MANAGEMENT VIEWS ====================

@login_required
def user_management(request):
    """Admin view for managing user approvals - superuser only"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    # Exclude superusers from user management - they don't need approval
    profiles = UserProfile.objects.select_related('user').filter(user__is_superuser=False)
    
    # Get search parameters
    search = request.GET.get('search')
    status = request.GET.get('status')
    department = request.GET.get('department')
    sort_by = request.GET.get('sort_by', '-created_at')
    
    # Apply filters
    if search:
        profiles = profiles.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(department__icontains=search)
        )
    
    if status:
        profiles = profiles.filter(status=status)
    
    if department:
        profiles = profiles.filter(department__icontains=department)
    
    # Apply sorting
    profiles = profiles.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(profiles, 25)
    page_number = request.GET.get('page')
    profiles = paginator.get_page(page_number)
    
    # Statistics (excluding superusers)
    total_users = UserProfile.objects.filter(user__is_superuser=False).count()
    pending_users = UserProfile.objects.filter(user__is_superuser=False, status='pending').count()
    approved_users = UserProfile.objects.filter(user__is_superuser=False, status='approved').count()
    rejected_users = UserProfile.objects.filter(user__is_superuser=False, status='rejected').count()
    suspended_users = UserProfile.objects.filter(user__is_superuser=False, status='suspended').count()
    
    context = {
        'profiles': profiles,
        'search_form': UserSearchForm(request.GET),
        'total_users': total_users,
        'pending_users': pending_users,
        'approved_users': approved_users,
        'rejected_users': rejected_users,
        'suspended_users': suspended_users,
    }
    
    return render(request, 'base/user_management.html', context)


@login_required
def reset_user_password(request, user_id):
    """Reset password for any user (superadmin only)"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    target_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Enhanced password validation
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(new_password) < 12:
            messages.error(request, 'Password must be at least 12 characters long.')
        elif not any(c.isupper() for c in new_password):
            messages.error(request, 'Password must contain at least one uppercase letter.')
        elif not any(c.islower() for c in new_password):
            messages.error(request, 'Password must contain at least one lowercase letter.')
        elif not any(c.isdigit() for c in new_password):
            messages.error(request, 'Password must contain at least one number.')
        elif not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in new_password):
            messages.error(request, 'Password must contain at least one special character.')
        else:
            target_user.set_password(new_password)
            target_user.save()
            
            # Log security event
            import logging
            logger = logging.getLogger('security')
            logger.info(f'Password reset by admin {request.user.username} for user {target_user.username}')
            
            messages.success(request, f'Password reset successfully for {target_user.username}!')
            return redirect('user-management')
    
    return render(request, 'base/password_reset.html', {'target_user': target_user})


@login_required
def delete_user(request, user_id):
    """Delete user account (superadmin only)"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    target_user = get_object_or_404(User, id=user_id)
    
    # Security checks
    if target_user.is_superuser:
        messages.error(request, 'Cannot delete superuser accounts.')
        return redirect('user-management')
    
    if target_user == request.user:
        messages.error(request, 'Cannot delete your own account.')
        return redirect('user-management')
    
    if request.method == 'POST':
        username = target_user.username
        
        # Log security event before deletion
        import logging
        logger = logging.getLogger('security')
        logger.warning(f'User {username} deleted by admin {request.user.username}')
        
        target_user.delete()
        messages.success(request, f'User {username} has been deleted successfully!')
        return redirect('user-management')
    
    return render(request, 'base/delete_user.html', {'target_user': target_user})


@login_required
def approve_user(request, user_id):
    """Approve or reject a user - superuser only"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('dashboard')
    
    try:
        profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('user-management')
    
    if request.method == 'POST':
        form = UserApprovalForm(request.POST, instance=profile)
        if form.is_valid():
            old_status = profile.status
            profile = form.save(commit=False)
            
            # Update approval information
            if profile.status == 'approved' and old_status != 'approved':
                profile.approved_by = request.user
                profile.approved_at = timezone.now()
                profile.rejection_reason = None  # Clear rejection reason if approved
                
                # Assign basic permissions to approved user
                user = profile.user
                user.user_permissions.add(
                    *[
                        'base.can_view_issue',
                        'base.can_add_issue',
                        'base.can_change_issue',
                        'base.can_export_issue',
                    ]
                )
                
                messages.success(request, f'User {profile.user.username} has been approved successfully!')
                
            elif profile.status == 'rejected':
                profile.approved_by = None
                profile.approved_at = None
                
                # Remove permissions from rejected user
                user = profile.user
                user.user_permissions.clear()
                
                messages.warning(request, f'User {profile.user.username} has been rejected.')
                
            elif profile.status == 'suspended':
                messages.warning(request, f'User {profile.user.username} has been suspended.')
                
            profile.save()
            
            return redirect('user-management')
    else:
        form = UserApprovalForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'base/approve_user.html', context)


@login_required
def user_profile(request):
    """User's own profile page"""
    # Check if user is approved (skip for superusers)
    if not request.user.is_superuser:
        try:
            profile = request.user.profile
            if not profile.is_approved:
                return redirect('pending-approval')
        except UserProfile.DoesNotExist:
            return redirect('pending-approval')
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user-profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'base/user_profile.html', context)


@login_required
def pending_approval(request):
    """Page shown to users pending approval"""
    try:
        profile = request.user.profile
        if profile.is_approved:
            return redirect('dashboard')
        elif profile.is_rejected:
            return render(request, 'base/rejected_user.html', {'profile': profile})
        else:
            return render(request, 'base/pending_approval.html', {'profile': profile})
    except UserProfile.DoesNotExist:
        return render(request, 'base/pending_approval.html')


@login_required
def welcome(request):
    """Welcome screen for all users with calendar"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    # Ensure user can access dashboard if approved or superuser
    can_access_dashboard = request.user.is_superuser or profile.is_approved
    
    context = {
        'profile': profile,
        'can_access_dashboard': can_access_dashboard,
    }
    # Add some basic counts for the metric cards (safe defaults)
    try:
        context.update({
            'total_issues': Issue.objects.count(),
            'open_issues': Issue.objects.filter(status__iexact='Open').count(),
            'user_tasks_count': Task.objects.filter(user=request.user).count() if request.user.is_authenticated else 0,
            'cr_count': ChangeRequest.objects.count(),
            'total_parts': Part.objects.filter(is_active=True).count(),
        })
    except Exception:
        # If models are not available for some reason, silently continue with defaults
        pass

    return render(request, 'base/contec_index.html', context)


@login_required
def metrics_api(request):
    """Return basic counts for dashboard metric cards as JSON."""
    try:
        data = {
            'total_issues': Issue.objects.count(),
            'open_issues': Issue.objects.filter(status__iexact='Open').count(),
            'user_tasks_count': Task.objects.filter(user=request.user).count() if request.user.is_authenticated else 0,
            'cr_count': ChangeRequest.objects.count(),
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def custom_logout(request):
    """Custom logout view with proper redirect"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


@login_required
def toggle_tips_preference(request):
    """Toggle user's tips preference"""
    if request.method == 'POST':
        show_tips = request.POST.get('show_tips') == '1'
        try:
            profile = request.user.profile
            profile.show_tips = show_tips
            profile.save()
            return JsonResponse({'status': 'success'})
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Profile not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
@require_http_methods(['POST'])
def toggle_tips_preference(request):
    """AJAX endpoint to toggle the user's preference for showing tips on issue create page."""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User profile not found.'}, status=404)

    value = request.POST.get('show_tips')
    # Accept 'true'/'false' or '1'/'0'
    if value is None:
        return JsonResponse({'status': 'error', 'message': 'Missing parameter show_tips.'}, status=400)

    val = value.lower() in ('1', 'true', 'yes', 'on')
    profile.show_tips = val
    profile.save()

    return JsonResponse({'status': 'success', 'show_tips': profile.show_tips})
