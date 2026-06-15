from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    Issue, Task, UserProfile, Customer, IssueCategory, ImpactCategory,
    INVOICE_TYPES, STATUS_CHOICES, AUTHORITY_CHOICES, USER_STATUS_CHOICES
)


class PositionForm(forms.Form):
    position = forms.CharField()


class IssueForm(forms.ModelForm):
    """Comprehensive form for Issue model with validation"""
    
    # Custom field widgets for better UX
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Describe the issue in detail...'
        }),
        required=False
    )
    
    # Use date-only fields shown/entered as MM/DD/YYYY for simpler UX
    identified_on = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        }),
        required=True,
        input_formats=['%m/%d/%Y', '%Y-%m-%d']
    )

    due_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        }),
        required=True,
        input_formats=['%m/%d/%Y', '%Y-%m-%d']
    )

    # Allow free-text entry for customer (user can type a new customer)
    customer = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter customer name (type to create new)'
        })
    )

    # Allow free-text entry for issue category (user can type a new category)
    issue_cat = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter issue category (type to create new)'
        })
    )
    
    revenue_impact = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        }),
        required=False
    )
    
    containment_action = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Describe containment actions taken...'
        }),
        required=False
    )
    
    corrective_action = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Describe corrective actions taken...'
        }),
        required=False
    )
    
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Additional remarks...'
        }),
        required=False
    )
    rebill_proof = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter details or proof for rebill/credit (invoice #, transaction ref, notes)'
        })
    )

    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Department (e.g., Billing, Ops)'
        })
    )

    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location (e.g., Site, Office, Node)'
        })
    )

    class Meta:
        model = Issue
        fields = [
            'customer', 'inv_type', 'issue_cat', 'description', 'identified_on',
            'identified_by', 'revenue_impact', 'impact_category', 'root_cause',
            'root_cause_owner', 'customer_received', 'impacted_customer',
            'containment_action', 'corrective_action', 'rebilled_credited',
                'rebill_proof', 'action_owner', 'due_date', 'status', 'approved', 'remarks', 'attachment',
            # department field must be included so ModelForm saves it to the model
            'department'
            ,'location'
        ]
        
        widgets = {
            'inv_type': forms.Select(attrs={'class': 'form-control form-select'}),
            # 'customer' and 'issue_cat' widgets intentionally omitted because IssueForm uses text inputs
            'identified_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your name...'
            }),
            'impact_category': forms.Select(attrs={
                'class': 'form-control form-select',
                'data-placeholder': 'Select an impact category...'
            }),
            'root_cause': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describe the root cause...'
            }),
            'root_cause_owner': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter root cause owner...'
            }),
            'customer_received': forms.Select(choices=[('', 'Please select'), ('Yes', 'Yes'), ('No', 'No')], attrs={'class': 'form-control'}),
            'impacted_customer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter impacted customer names (free text)...'
            }),
            'rebilled_credited': forms.Select(choices=[('', 'Please select'), ('Yes', 'Yes'), ('No', 'No')], attrs={'class': 'form-control'}),
            'rebill_proof': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter details or proof for rebill/credit (invoice #, transaction ref, notes)'}),
            'action_owner': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter action owner...'
            }),
            'status': forms.Select(attrs={'class': 'form-control form-select'}),
            'approved': forms.Select(attrs={'class': 'form-control form-select'}),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.xlsx,.jpg,.jpeg,.png,.gif'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter only active lookup table entries
        self.fields['impact_category'].queryset = ImpactCategory.objects.filter(is_active=True)

        # When editing an existing issue, show the *names* for customer and
        # issue category instead of their underlying integer IDs.
        #
        # Django's ModelForm machinery will have already populated
        # self.initial['customer'] / self.initial['issue_cat'] with the
        # related object's primary key (e.g. 1, 2).  We need to overwrite
        # those values with the human‑readable names so that the text inputs
        # display what the user originally typed.
        if self.instance.pk:
            if getattr(self.instance, 'customer', None):
                name = self.instance.customer.name
                self.initial['customer'] = name
                self.fields['customer'].initial = name
            if getattr(self.instance, 'issue_cat', None):
                name = self.instance.issue_cat.name
                self.initial['issue_cat'] = name
                self.fields['issue_cat'].initial = name
        else:
            # Set initial values for dates when creating a new issue
            from django.utils import timezone
            now = timezone.now()
            # Format for MM/DD/YYYY date-only input
            self.initial['identified_on'] = now.strftime('%m/%d/%Y')
            self.initial['due_date'] = (now + timezone.timedelta(days=7)).strftime('%m/%d/%Y')
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if 'form-control' not in field.widget.attrs.get('class', ''):
                # Some widgets (like Select) may already have class applied via widgets dict
                field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.widget.attrs.update({'required': True})

    def clean(self):
        cleaned_data = super().clean()
        identified_on = cleaned_data.get('identified_on')
        due_date = cleaned_data.get('due_date')
        
        # Validate identified_on is not in the future
        if identified_on:
            try:
                # Get today's date at midnight
                today = timezone.now().date()
                identified_date = identified_on.date() if hasattr(identified_on, 'date') else identified_on
                
                if identified_date > today:
                    self.add_error('identified_on', "Identified On date cannot be in the future. It must be today or earlier.")
            except Exception as e:
                print(f"DEBUG: Identified On date validation error: {e}")
                # Don't fail the form if date comparison fails
                pass
        
        # Validate due date is not before identified date (simplified)
        if identified_on and due_date:
            try:
                # Convert to date only for comparison to avoid timezone issues
                identified_date = identified_on.date() if hasattr(identified_on, 'date') else identified_on
                due_date_only = due_date.date() if hasattr(due_date, 'date') else due_date
                
                if due_date_only < identified_date:
                    self.add_error('due_date', "Due date cannot be before the identified date.")
            except Exception as e:
                print(f"DEBUG: Date validation error: {e}")
                # Don't fail the form if date comparison fails
                pass
        
        # Validate revenue impact
        revenue_impact = cleaned_data.get('revenue_impact')
        if revenue_impact is not None and revenue_impact < 0:
            self.add_error('revenue_impact', "Revenue impact cannot be negative.")
        # Normalize checkbox booleans to Yes/No strings for storage
        for key in ('customer_received', 'rebilled_credited'):
            val = cleaned_data.get(key)
            # Checkbox input may come as True/False or 'on' from HTML
            if isinstance(val, bool):
                cleaned_data[key] = 'Yes' if val else 'No'
            elif isinstance(val, str):
                cleaned_data[key] = 'Yes' if val.lower() in ('true', '1', 'yes', 'on') else 'No'
        
        return cleaned_data

    def clean_identified_by(self):
        identified_by = self.cleaned_data.get('identified_by')
        if identified_by and len(identified_by.strip()) >= 2:
            return identified_by.strip()
        elif not identified_by:
            raise ValidationError("This field is required.")
        else:
            raise ValidationError("Must contain at least 2 characters.")

    def clean_root_cause(self):
        root_cause = self.cleaned_data.get('root_cause')
        if root_cause and len(root_cause.strip()) >= 5:
            return root_cause.strip()
        elif not root_cause:
            raise ValidationError("This field is required.")
        else:
            raise ValidationError("Must be at least 5 characters long.")
    
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (5MB limit for production)
            if attachment.size > 5 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 5MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.docx', '.xlsx', '.jpg', '.jpeg', '.png']
            file_extension = attachment.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError("File type not allowed. Please upload PDF, DOCX, XLSX, JPG, or PNG files.")
            
            # Skip MIME check for development
        
        return attachment

    def clean_customer(self):
        """Accept free-text customer; resolve to Customer instance (create if missing)."""
        cust_value = self.cleaned_data.get('customer')
        if not cust_value or not cust_value.strip():
            raise ValidationError("This field is required.")
        name = cust_value.strip()
        # Try to find existing customer (case-insensitive)
        try:
            customer = Customer.objects.filter(name__iexact=name).first()
            if customer:
                return customer
            # Create new customer as active
            customer = Customer.objects.create(name=name, is_active=True)
            return customer
        except Exception as e:
            raise ValidationError(f"Unable to resolve or create customer: {e}")

    def clean_issue_cat(self):
        """Accept free-text category; resolve to IssueCategory instance (create if missing)."""
        cat_value = self.cleaned_data.get('issue_cat')
        if not cat_value or not cat_value.strip():
            raise ValidationError("This field is required.")
        name = cat_value.strip()
        # Try to find existing category (case-insensitive)
        try:
            category = IssueCategory.objects.filter(name__iexact=name).first()
            if category:
                return category
            # Create new category as active
            category = IssueCategory.objects.create(name=name, is_active=True)
            return category
        except Exception as e:
            raise ValidationError(f"Unable to resolve or create category: {e}")


class IssueSearchForm(forms.Form):
    """Form for searching and filtering issues"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by description, root cause, or identified by...',
            'style': 'width: 300px;'
        })
    )
    
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        required=False,
        empty_label='All Customers',
        widget=forms.Select(attrs={'class': 'form-control form-select'})
    )
    
    inv_type = forms.ChoiceField(
        choices=[('', 'All Invoice Types')] + list(INVOICE_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-select'})
    )
    
    issue_cat = forms.ModelChoiceField(
        queryset=IssueCategory.objects.filter(is_active=True),
        required=False,
        empty_label='All Issue Categories',
        widget=forms.Select(attrs={'class': 'form-control form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-select'})
    )
    
    impact_category = forms.ModelChoiceField(
        queryset=ImpactCategory.objects.filter(is_active=True),
        required=False,
        empty_label='All Impact Categories',
        widget=forms.Select(attrs={'class': 'form-control form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        }),
        input_formats=['%m/%d/%Y', '%Y-%m-%d']
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/DD/YYYY',
            'autocomplete': 'off'
        }),
        input_formats=['%m/%d/%Y', '%Y-%m-%d']
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('id', 'Oldest First (by ID)'),
            ('-id', 'Newest First (by ID)'),
            ('identified_on', 'Identified On (Oldest)'),
            ('-identified_on', 'Identified On (Newest)'),
            ('issue_cat', 'Issue Category (A-Z)'),
            ('-issue_cat', 'Issue Category (Z-A)'),
            ('department', 'Department (A-Z)'),
            ('-department', 'Department (Z-A)'),
            ('location', 'Location (A-Z)'),
            ('-location', 'Location (Z-A)'),
            ('inv_type', 'Invoice Type (A-Z)'),
            ('-inv_type', 'Invoice Type (Z-A)'),
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('due_date', 'Due Date (Asc)'),
            ('-due_date', 'Due Date (Desc)'),
            ('customer', 'Customer (A-Z)'),
            ('-customer', 'Customer (Z-A)'),
            ('status', 'Status (A-Z)'),
            ('-status', 'Status (Z-A)'),
            ('revenue_impact', 'Revenue Impact (Low-High)'),
            ('-revenue_impact', 'Revenue Impact (High-Low)'),
        ],
        required=False,
        initial='id',
        widget=forms.Select(attrs={'class': 'form-control form-select'})
    )


class EmailForm(forms.Form):
    """Form for email popup functionality"""
    
    to_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'recipient@example.com'
        })
    )
    
    cc_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'cc@example.com (optional)'
        })
    )
    
    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email subject...'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8,
            'class': 'form-control',
            'placeholder': 'Your message...'
        })
    )
    
    include_issue_details = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class CSVUploadForm(forms.Form):
    """Form for CSV file upload"""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx',
            'id': 'csv-file'
        })
    )
    server_path = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional server file path relative to IMPORT_DIR (e.g. uploads/myfile.csv)'
        })
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            name = csv_file.name.lower()
            if not (name.endswith('.csv') or name.endswith('.xlsx') or name.endswith('.xls')):
                raise ValidationError("File must be a CSV or Excel (.xlsx/.xls) file.")
            if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("File size cannot exceed 5MB.")
        return csv_file


class UserApprovalForm(forms.ModelForm):
    """Form for admin to approve/reject users"""
    
    can_access_approvals = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can Access CR Approvals',
        help_text='Allow this user to access and approve Change Requests'
    )
    
    can_access_issues = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can Access Issues',
        help_text='Allow this user to access the Issue Management system'
    )
    
    can_access_parts = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can Access Parts Price Book',
        help_text='Allow this user to access the Parts Price Book system'
    )
    
    can_access_cr = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can Access Change Requests',
        help_text='Allow this user to access the Change Request system'
    )
    
    can_access_tasks = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can Access Tasks',
        help_text='Allow this user to access the Task Management system'
    )
    
    can_access_reports = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Can Access Reports',
        help_text='Allow this user to access reporting features'
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'status', 'department', 'phone_number', 'notes', 'rejection_reason', 
            'can_access_approvals', 'can_access_issues', 'can_access_parts', 
            'can_access_cr', 'can_access_tasks', 'can_access_reports'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department...'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number...'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Admin notes...'
            }),
            'rejection_reason': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Reason for rejection (if applicable)...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make rejection_reason required only if status is rejected
        if self.instance and self.instance.status == 'rejected':
            self.fields['rejection_reason'].required = True

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if status == 'rejected' and not rejection_reason:
            raise ValidationError("Rejection reason is required when rejecting a user.")
        
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """Form for users to update their profile information"""
    
    class Meta:
        model = UserProfile
        fields = ['department', 'phone_number']
        widgets = {
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your department...'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number...'
            }),
        }


class UserSearchForm(forms.Form):
    """Form for searching and filtering users"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by username, email, or department...',
            'style': 'width: 300px;'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(USER_STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by department...'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('user__username', 'Username (A-Z)'),
            ('-user__username', 'Username (Z-A)'),
            ('status', 'Status (A-Z)'),
            ('-status', 'Status (Z-A)'),
            ('department', 'Department (A-Z)'),
            ('-department', 'Department (Z-A)'),
        ],
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
