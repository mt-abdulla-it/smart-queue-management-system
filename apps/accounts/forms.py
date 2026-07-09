"""
Accounts Forms.

Forms for user registration, login, profile update, and password management.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form using email instead of username."""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'nic')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form."""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'nic', 'profile_image')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    """Form for users to update their profile."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'nic', 'profile_image')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form using email."""
    
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autofocus': True})
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
