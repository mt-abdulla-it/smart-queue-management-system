from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, StaffProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('user_avatar', 'email', 'full_name_display', 'role_badge', 'status_badge', 'is_email_verified', 'date_joined')
    list_filter = ('role', 'is_active', 'is_email_verified')
    search_fields = ('email', 'first_name', 'last_name', 'nic')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'nic', 'profile_image')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_email_verified', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    def full_name_display(self, obj):
        name = obj.get_full_name()
        return name if name else "—"
    full_name_display.short_description = "Full Name"

    def user_avatar(self, obj):
        initials = (obj.first_name[:1] + obj.last_name[:1]).upper() if (obj.first_name and obj.last_name) else obj.email[:2].upper()
        bg_colors = {'ADMIN': '#6366f1', 'STAFF': '#0ea5e9', 'USER': '#10b981'}
        color = bg_colors.get(obj.role, '#6b7280')
        return format_html(
            '<div style="width:36px;height:36px;border-radius:50%;background:{};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;box-shadow:0 2px 8px rgba(0,0,0,0.15);">{}</div>',
            color, initials
        )
    user_avatar.short_description = "Avatar"

    def role_badge(self, obj):
        role_styles = {
            'ADMIN': 'background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3);',
            'STAFF': 'background:rgba(14,165,233,0.15);color:#38bdf8;border:1px solid rgba(14,165,233,0.3);',
            'USER': 'background:rgba(16,185,129,0.15);color:#34d399;border:1px solid rgba(16,185,129,0.3);'
        }
        style = role_styles.get(obj.role, 'background:#374151;color:#9ca3af;')
        return format_html(
            '<span style="padding:4px 12px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;{};">{}</span>',
            style, obj.get_role_display()
        )
    role_badge.short_description = "Role"

    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;background:rgba(34,197,94,0.15);color:#22c55e;border:1px solid rgba(34,197,94,0.3);"><i class="fas fa-check-circle" style="margin-right:4px;"></i>Active</span>')
        return format_html('<span style="padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.3);"><i class="fas fa-times-circle" style="margin-right:4px;"></i>Inactive</span>')
    status_badge.short_description = "Status"


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'branch', 'department', 'is_available')
    list_filter = ('is_available', 'branch', 'department')
    search_fields = ('user__email', 'employee_id')

