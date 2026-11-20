from django.contrib import admin

from .models import Route, RouteStop


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1
    ordering = ('sequence',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'direction', 'is_active')
    list_filter = ('direction', 'is_active')
    search_fields = ('name', 'description')
    inlines = [RouteStopInline]


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('name', 'route', 'sequence', 'latitude', 'longitude', 'is_active')
    list_filter = ('route', 'is_active')
    search_fields = ('name', 'route__name')
    ordering = ('route', 'sequence')
