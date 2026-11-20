from django.db import models


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        VAN = 'van', 'Van'
        BUS = 'bus', 'Bus'
        CAR = 'car', 'Car'

    name = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=30, unique=True)
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.VAN,
    )
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'vehicles'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.plate_number})'
