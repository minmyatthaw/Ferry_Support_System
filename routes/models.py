from django.db import models


class Route(models.Model):
    class Direction(models.TextChoices):
        MORNING_PICKUP = 'morning_pickup', 'Morning pickup'
        EVENING_RETURN = 'evening_return', 'Evening return'

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    direction = models.CharField(
        max_length=20,
        choices=Direction.choices,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'routes'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_direction_display()})'


class RouteStop(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='stops',
    )
    name = models.CharField(max_length=150)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    sequence = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'route_stops'
        ordering = ['route', 'sequence']
        constraints = [
            models.UniqueConstraint(
                fields=['route', 'sequence'],
                name='uniq_route_stop_sequence',
            ),
        ]

    def __str__(self):
        return f'{self.route.name} #{self.sequence}: {self.name}'
