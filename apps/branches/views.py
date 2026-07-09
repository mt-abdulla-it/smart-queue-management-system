"""
Branch Management Views.

Only ADMIN users should access these views.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from apps.core.mixins import RoleRequiredMixin

from .models import Branch, Department, Service
from .forms import BranchForm, DepartmentForm, ServiceForm

# ---------- Branch Views ---------- #

class BranchListView(RoleRequiredMixin, ListView):
    model = Branch
    template_name = 'branches/branch_list.html'
    context_object_name = 'branches'
    allowed_roles = ['ADMIN']
    
class BranchCreateView(RoleRequiredMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'branches/branch_form.html'
    success_url = reverse_lazy('branches:branch_list')
    allowed_roles = ['ADMIN']

    def form_valid(self, form):
        messages.success(self.request, 'Branch created successfully.')
        return super().form_valid(form)

class BranchUpdateView(RoleRequiredMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'branches/branch_form.html'
    success_url = reverse_lazy('branches:branch_list')
    allowed_roles = ['ADMIN']

    def form_valid(self, form):
        messages.success(self.request, 'Branch updated successfully.')
        return super().form_valid(form)

class BranchDeleteView(RoleRequiredMixin, DeleteView):
    model = Branch
    template_name = 'branches/branch_confirm_delete.html'
    success_url = reverse_lazy('branches:branch_list')
    allowed_roles = ['ADMIN']

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Branch deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ---------- Department Views ---------- #

class DepartmentListView(RoleRequiredMixin, ListView):
    model = Department
    template_name = 'branches/department_list.html'
    context_object_name = 'departments'
    allowed_roles = ['ADMIN']
    
class DepartmentCreateView(RoleRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'branches/department_form.html'
    success_url = reverse_lazy('branches:department_list')
    allowed_roles = ['ADMIN']

    def form_valid(self, form):
        messages.success(self.request, 'Department created successfully.')
        return super().form_valid(form)

class DepartmentUpdateView(RoleRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'branches/department_form.html'
    success_url = reverse_lazy('branches:department_list')
    allowed_roles = ['ADMIN']

    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully.')
        return super().form_valid(form)


# ---------- Service Views ---------- #

class ServiceListView(RoleRequiredMixin, ListView):
    model = Service
    template_name = 'branches/service_list.html'
    context_object_name = 'services'
    allowed_roles = ['ADMIN']
    
class ServiceCreateView(RoleRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'branches/service_form.html'
    success_url = reverse_lazy('branches:service_list')
    allowed_roles = ['ADMIN']

    def form_valid(self, form):
        messages.success(self.request, 'Service created successfully.')
        return super().form_valid(form)

class ServiceUpdateView(RoleRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'branches/service_form.html'
    success_url = reverse_lazy('branches:service_list')
    allowed_roles = ['ADMIN']

    def form_valid(self, form):
        messages.success(self.request, 'Service updated successfully.')
        return super().form_valid(form)
