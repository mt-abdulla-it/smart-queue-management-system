"""
Feedback Forms.
"""
from django import forms
from .models import Feedback
from apps.branches.models import Branch

class FeedbackForm(forms.ModelForm):
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.filter(is_active=True),
        empty_label="Select Branch",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    RATING_CHOICES = [(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(5, 0, -1)]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Feedback
        fields = ['branch', 'rating', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about your experience...'}),
        }
