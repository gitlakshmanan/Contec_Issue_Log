
from django import forms
from .models import PartPrice, Customer, PONumber, SONumber
from django.contrib.auth.models import User
import datetime

class PartPriceForm(forms.ModelForm):
    class Meta:
        model = PartPrice
        fields = ['customer', 'partnumber', 'price', 'startdate', 'enddate', 
                  'margin', 'po_number', 'so_number', 'remarks']
        widgets = {
            'startdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'enddate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'po_number': forms.Select(attrs={'class': 'form-select'}),
            'so_number': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in ['price', 'margin']:
                field.widget.attrs['step'] = '0.01'
    
    def clean(self):
        cleaned_data = super().clean()
        startdate = cleaned_data.get('startdate')
        enddate = cleaned_data.get('enddate')
        
        if enddate and startdate and enddate < startdate:
            raise forms.ValidationError("End date cannot be earlier than start date.")
        
        return cleaned_data

class PartPriceReviewForm(forms.ModelForm):
    comments = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False)
    
    class Meta:
        model = PartPrice
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class SearchForm(forms.Form):
    partnumber = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by Part Number',
            'id': 'searchInput'
        })
    )
    customer = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by Customer'
        })
    )

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PONumberForm(forms.ModelForm):
    class Meta:
        model = PONumber
        fields = ['po_number']
        widgets = {
            'po_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SONumberForm(forms.ModelForm):
    class Meta:
        model = SONumber
        fields = ['so_number']
        widgets = {
            'so_number': forms.TextInput(attrs={'class': 'form-control'}),
        }