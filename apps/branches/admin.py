"""Branches admin."""
from django.contrib import admin
from .models import Branch, Department, Service


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'district', 'is_active')
    list_filter = ('is_active', 'district')
    search_fields = ('name', 'code', 'city')
    inlines = [DepartmentInline]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'branch', 'is_active')
    list_filter = ('is_active', 'branch')
    search_fields = ('name', 'code')
    inlines = [ServiceInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'prefix', 'department', 'avg_service_time_minutes', 'max_daily_tokens', 'is_active')
    list_filter = ('is_active', 'department__branch')
    search_fields = ('name', 'code', 'prefix')
