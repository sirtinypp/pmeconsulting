from django import forms
from .models import ServiceInquiry

class ServiceInquiryForm(forms.ModelForm):
    class Meta:
        model = ServiceInquiry
        fields = ['name', 'email', 'phone', 'current_job', 'background', 'language_goal', 'service_requested', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number (Optional)'}),
            'current_job': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Current Job/Professional Status'}),
            'background': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Educational or Clinical Background'}),
            'language_goal': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'What is your German Language/Career goal?'}),
            'service_requested': forms.Select(attrs={'class': 'form-input'}),
            'message': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Any specific details or questions?', 'rows': 4}),
        }
