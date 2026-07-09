"""
Queue Forms.
"""
from django import forms
from .models import QueueToken
from apps.branches.models import Branch, Department, Service

class QueueBookingForm(forms.ModelForm):
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.filter(is_active=True),
        empty_label="Select Branch",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_branch'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_department'})
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        empty_label="Select Service",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_service'})
    )

    class Meta:
        model = QueueToken
        fields = ['branch', 'department', 'service']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # AJAX handling for dependent dropdowns
        if 'branch' in self.data:
            try:
                branch_id = int(self.data.get('branch'))
                self.fields['department'].queryset = Department.objects.filter(branch_id=branch_id, is_active=True)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty queryset
        
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['service'].queryset = Service.objects.filter(department_id=department_id, is_active=True)
            except (ValueError, TypeError):
                pass
