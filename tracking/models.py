from django.db import models


class VehicleLocation(models.Model):
    trip = models.ForeignKey(
        'trips.Trip',
        on_delete=models.CASCADE,
        related_name='vehicle_locations',
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='GPS accuracy in meters',
    )
    speed = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Speed in km/h',
    )
    recorded_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'vehicle_locations'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['trip', 'recorded_at']),
        ]

    def __str__(self):
        return f'Trip {self.trip_id} @ {self.recorded_at}'


class LocationSharingSession(models.Model):
    employee = models.ForeignKey(
        'users.EmployeeProfile',
        on_delete=models.CASCADE,
        related_name='location_sharing_sessions',
    )
    trip = models.ForeignKey(
        'trips.Trip',
        on_delete=models.CASCADE,
        related_name='location_sharing_sessions',
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'location_sharing_sessions'
        indexes = [
            models.Index(fields=['employee', 'trip', 'is_active']),
        ]

    def __str__(self):
        state = 'active' if self.is_active else 'ended'
        return f'Session {self.pk} ({state}) for {self.employee} on trip {self.trip_id}'


class EmployeeLocation(models.Model):
    session = models.ForeignKey(
        LocationSharingSession,
        on_delete=models.CASCADE,
        related_name='locations',
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    recorded_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'employee_locations'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['session', 'recorded_at']),
        ]

    def __str__(self):
        return f'Session {self.session_id} @ {self.recorded_at}'
