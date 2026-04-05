from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    primary_interest = forms.ChoiceField(
        choices=[('', 'What is your primary interest?')] + list(
            [('DEEP_ANALYSIS', 'Direct Career Consultation'),
             ('CV_LETTER', 'CV & Motivation Letter'),
             ('CHECKLIST', 'Personalized Checklist'),
             ('PROGRAM', 'Full German Training Program'),
             ('EXPLORING', 'Just Exploring / Passing By')]
        ),
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'primary_interest')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.GUEST  # Explicitly set to GUEST on signup
        if commit:
            user.save()
        return user
