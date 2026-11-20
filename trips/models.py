from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Trip(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        BOARDING = 'boarding', 'Boarding'
        IN_PROGRESS = 'in_progress', 'In progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    route = models.ForeignKey(
        'routes.Route',
        on_delete=models.PROTECT,
        related_name='trips',
    )
    driver = models.ForeignKey(
        'users.DriverProfile',
        on_delete=models.PROTECT,
        related_name='trips',
    )
    vehicle = models.ForeignKey(
        'fleet.Vehicle',
        on_delete=models.PROTECT,
        related_name='trips',
    )
    trip_date = models.DateField(db_index=True)
    scheduled_start = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trips'
        ordering = ['-trip_date', '-scheduled_start']
        indexes = [
            models.Index(fields=['trip_date', 'status']),
        ]

    def __str__(self):
        return f'Trip {self.pk}: {self.route.name} on {self.trip_date}'


class TripStop(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ARRIVED = 'arrived', 'Arrived'
        COMPLETED = 'completed', 'Completed'
        SKIPPED = 'skipped', 'Skipped'

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='stops',
    )
    route_stop = models.ForeignKey(
        'routes.RouteStop',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trip_stops',
    )
    name = models.CharField(max_length=150)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    sequence = models.PositiveIntegerField()
    confirmed_eta = models.DateTimeField(null=True, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        db_table = 'trip_stops'
        ordering = ['trip', 'sequence']
        constraints = [
            models.UniqueConstraint(
                fields=['trip', 'sequence'],
                name='uniq_trip_stop_sequence',
            ),
        ]

    def __str__(self):
        return f'Trip {self.trip_id} #{self.sequence}: {self.name}'


class PickupPreference(models.Model):
    """Recurring preferred stop for an employee on a route (weekdays 0=Mon .. 6=Sun)."""

    employee = models.ForeignKey(
        'users.EmployeeProfile',
        on_delete=models.CASCADE,
        related_name='pickup_preferences',
    )
    route = models.ForeignKey(
        'routes.Route',
        on_delete=models.CASCADE,
        related_name='pickup_preferences',
    )
    route_stop = models.ForeignKey(
        'routes.RouteStop',
        on_delete=models.PROTECT,
        related_name='pickup_preferences',
    )
    days_of_week = models.JSONField(
        default=list,
        help_text='List of weekday integers: 0=Monday … 6=Sunday',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pickup_preferences'
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'route'],
                name='uniq_employee_route_preference',
            ),
        ]

    def clean(self):
        if self.route_stop_id and self.route_id:
            if self.route_stop.route_id != self.route_id:
                raise ValidationError(
                    {'route_stop': 'Route stop must belong to the selected route.'}
                )
        if not isinstance(self.days_of_week, list):
            raise ValidationError({'days_of_week': 'Must be a list of weekday integers.'})
        invalid = [d for d in self.days_of_week if not isinstance(d, int) or d < 0 or d > 6]
        if invalid:
            raise ValidationError({'days_of_week': 'Weekdays must be integers from 0 to 6.'})

    def __str__(self):
        return f'{self.employee} → {self.route_stop.name} on {self.route.name}'


class PickupSkip(models.Model):
    """Skip a specific trip despite an active recurring preference."""

    employee = models.ForeignKey(
        'users.EmployeeProfile',
        on_delete=models.CASCADE,
        related_name='pickup_skips',
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='pickup_skips',
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pickup_skips'
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'trip'],
                name='uniq_employee_trip_skip',
            ),
        ]

    def __str__(self):
        return f'{self.employee} skips trip {self.trip_id}'


class PickupRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        CONFIRMED = 'confirmed', 'Confirmed'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
        PICKED_UP = 'picked_up', 'Picked up'
        NO_SHOW = 'no_show', 'No show'
        CANCELLED = 'cancelled', 'Cancelled'
        SKIPPED = 'skipped', 'Skipped'

    ACTIVE_STATUSES = {
        Status.REQUESTED,
        Status.CONFIRMED,
        Status.ACKNOWLEDGED,
        Status.PICKED_UP,
    }

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='pickup_requests',
    )
    trip_stop = models.ForeignKey(
        TripStop,
        on_delete=models.PROTECT,
        related_name='pickup_requests',
    )
    employee = models.ForeignKey(
        'users.EmployeeProfile',
        on_delete=models.CASCADE,
        related_name='pickup_requests',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True,
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'pickup_requests'
        constraints = [
            models.UniqueConstraint(
                fields=['trip', 'employee'],
                name='uniq_employee_pickup_per_trip',
            ),
        ]
        indexes = [
            models.Index(fields=['trip', 'status']),
            models.Index(fields=['employee', 'status']),
        ]

    def clean(self):
        if self.trip_stop_id and self.trip_id:
            if self.trip_stop.trip_id != self.trip_id:
                raise ValidationError(
                    {'trip_stop': 'Trip stop must belong to the selected trip.'}
                )
        if self.trip_id and self.status in self.ACTIVE_STATUSES:
            active_count = (
                PickupRequest.objects.filter(
                    trip_id=self.trip_id,
                    status__in=self.ACTIVE_STATUSES,
                )
                .exclude(pk=self.pk)
                .count()
            )
            capacity = self.trip.vehicle.capacity
            if active_count + 1 > capacity:
                raise ValidationError(
                    f'Trip capacity exceeded ({capacity}). Cannot add another passenger.'
                )

    def __str__(self):
        return f'{self.employee} on trip {self.trip_id} @ {self.trip_stop.name}'


class PickupRequestEvent(models.Model):
    pickup_request = models.ForeignKey(
        PickupRequest,
        on_delete=models.CASCADE,
        related_name='events',
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pickup_request_events',
    )
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pickup_request_events'
        ordering = ['-created_at']

    def __str__(self):
        return f'Request {self.pickup_request_id}: {self.old_status} → {self.new_status}'


class EtaRecord(models.Model):
    class EtaType(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        DYNAMIC = 'dynamic', 'Dynamic'

    class Source(models.TextChoices):
        DRIVER = 'driver', 'Driver'
        ROUTING_SERVICE = 'routing_service', 'Routing service'
        SYSTEM = 'system', 'System'

    trip_stop = models.ForeignKey(
        TripStop,
        on_delete=models.CASCADE,
        related_name='eta_records',
    )
    pickup_request = models.ForeignKey(
        PickupRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='eta_records',
    )
    eta_type = models.CharField(max_length=20, choices=EtaType.choices)
    estimated_arrival = models.DateTimeField()
    source = models.CharField(
        max_length=30,
        choices=Source.choices,
        default=Source.SYSTEM,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'eta_records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trip_stop', 'eta_type', 'created_at']),
        ]

    def __str__(self):
        return f'{self.eta_type} ETA for stop {self.trip_stop_id}: {self.estimated_arrival}'
