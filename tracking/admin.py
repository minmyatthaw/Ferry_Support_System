from django.contrib import admin

from .models import EmployeeLocation, LocationSharingSession, VehicleLocation


@admin.register(VehicleLocation)
class VehicleLocationAdmin(admin.ModelAdmin):
    list_display = ('trip', 'latitude', 'longitude', 'speed', 'accuracy', 'recorded_at')
    list_filter = ('trip',)
    search_fields = ('trip__id',)
    date_hierarchy = 'recorded_at'


@admin.register(LocationSharingSession)
class LocationSharingSessionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'trip', 'started_at', 'ended_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('employee__employee_code', 'trip__id')


@admin.register(EmployeeLocation)
class EmployeeLocationAdmin(admin.ModelAdmin):
    list_display = ('session', 'latitude', 'longitude', 'recorded_at')
    search_fields = ('session__id',)
    date_hierarchy = 'recorded_at'
