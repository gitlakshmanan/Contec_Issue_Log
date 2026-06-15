from django import forms
from contec_cr.models import ChangeRequest

class ChangeRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-control form-select'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control form-control-file'
            
            # Add placeholder text
            if field_name == 'effecting_app':
                field.widget.attrs['placeholder'] = 'Enter the name of the application being changed'
            elif field_name == 'description':
                field.widget.attrs['placeholder'] = 'Provide a detailed description of the change'
        
        # Restrict status choices to draft and submitted only for user creation/editing
        if 'status' in self.fields:
            self.fields['status'].choices = [
                ('draft', 'Draft'),
                ('submitted', 'Submitted'),
            ]

    class Meta:
        model = ChangeRequest
        fields = [
            'effecting_app', 'cr_raised_by', 'cr_raised_on', 'department', 'job_name', 'priority',
            'description', 'details_pre_cr', 'details_post_cr',
            'back_up', 'process_manager', 'resource_name',
            'start_date', 'identified_risks', 'end_date',
            'tested_on', 'validated_on', 'result_state', 'attachment',
            'change_benefits', 'impacting_customer', 'remarks',
            'status'
        ]
        widgets = {
            'cr_raised_on': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'tested_on': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'validated_on': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Provide a detailed description of the change request'
            }),
            'details_pre_cr': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describe the state before the change'
            }),
            'details_post_cr': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describe the expected state after the change'
            }),
            'identified_risks': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'List any identified risks and mitigation plans'
            }),
            'change_benefits': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describe the benefits of this change'
            }),
            'remarks': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Any additional remarks or notes'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.xlsx,.txt,.jpg,.jpeg,.png,.gif,.zip,.rar'
            })
        }
        
        labels = {
            'effecting_app': 'Effecting Application',
            'cr_raised_by': 'Raised by',
            'cr_raised_on': 'Raised Date',
            'department': 'Department',
            'job_name': 'Job Name',
            'priority': 'Priority',
            'back_up': 'Backup Plan',
            'process_manager': 'Process Manager',
            'resource_name': 'Assigned Resource',
            'details_pre_cr': 'Pre-Change Details',
            'details_post_cr': 'Post-Change Details',
            'impacting_customer': 'Impacted Customer',
        }
        
        help_texts = {
            'effecting_app': 'Name of the application or system being changed',
            'back_up': 'Describe the backup/rollback plan in case of issues',
            'identified_risks': 'List potential risks and their mitigation strategies',
            'impacting_customer': 'List of customers affected by this change',
            'attachment': 'Upload supporting documents (PDF, DOCX, XLSX, TXT, images) up to 5MB',
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (5MB limit)
            if attachment.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 5MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.docx', '.xlsx', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar']
            file_extension = '.' + attachment.name.lower().split('.')[-1]
            if file_extension not in allowed_extensions:
                raise forms.ValidationError("File type not allowed. Please upload PDF, DOCX, XLSX, TXT, images, or archive files.")
        
        return attachment

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = ChangeRequest
        fields = ['cr_approved_by', 'cr_approved_on', 'status']
        widgets = {
            'cr_approved_on': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cr_approved_by': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict status choices to approved and rejected only
        self.fields['status'].choices = [
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ]