from django.contrib import admin

from .models import (
    EtaRecord,
    PickupPreference,
    PickupRequest,
    PickupRequestEvent,
    PickupSkip,
    Trip,
    TripStop,
)


class TripStopInline(admin.TabularInline):
    model = TripStop
    extra = 0
    ordering = ('sequence',)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'route',
        'trip_date',
        'scheduled_start',
        'driver',
        'vehicle',
        'status',
    )
    list_filter = ('status', 'trip_date', 'route')
    search_fields = ('route__name', 'driver__user__username', 'vehicle__plate_number')
    date_hierarchy = 'trip_date'
    inlines = [TripStopInline]


@admin.register(TripStop)
class TripStopAdmin(admin.ModelAdmin):
    list_display = ('name', 'trip', 'sequence', 'status', 'confirmed_eta', 'arrived_at')
    list_filter = ('status',)
    search_fields = ('name', 'trip__id')


@admin.register(PickupPreference)
class PickupPreferenceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'route', 'route_stop', 'days_of_week', 'is_active')
    list_filter = ('is_active', 'route')
    search_fields = ('employee__employee_code', 'route__name', 'route_stop__name')


@admin.register(PickupSkip)
class PickupSkipAdmin(admin.ModelAdmin):
    list_display = ('employee', 'trip', 'created_at')
    search_fields = ('employee__employee_code', 'trip__id')


@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'trip',
        'trip_stop',
        'status',
        'requested_at',
        'picked_up_at',
    )
    list_filter = ('status',)
    search_fields = ('employee__employee_code', 'trip__id', 'trip_stop__name')


@admin.register(PickupRequestEvent)
class PickupRequestEventAdmin(admin.ModelAdmin):
    list_display = ('pickup_request', 'old_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('new_status',)
    search_fields = ('pickup_request__id',)


@admin.register(EtaRecord)
class EtaRecordAdmin(admin.ModelAdmin):
    list_display = (
        'trip_stop',
        'pickup_request',
        'eta_type',
        'estimated_arrival',
        'source',
        'created_at',
    )
    list_filter = ('eta_type', 'source')
