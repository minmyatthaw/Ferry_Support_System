from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import DriverProfile, EmployeeProfile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Ferry profile', {'fields': ('phone', 'role')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Ferry profile', {'fields': ('phone', 'role')}),
    )


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'user', 'department', 'position')
    search_fields = ('employee_code', 'user__username', 'department', 'position')
    list_filter = ('department',)


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'license_expiry', 'employment_status')
    list_filter = ('employment_status',)
    search_fields = ('user__username', 'license_number')
