from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        EMPLOYEE = 'employee', 'Employee'
        DRIVER = 'driver', 'Driver'

    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.username} ({self.role})'


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
    )
    employee_code = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'employee_profiles'

    def __str__(self):
        return f'{self.employee_code} - {self.user.get_full_name() or self.user.username}'


class DriverProfile(models.Model):
    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='driver_profile',
    )
    license_number = models.CharField(max_length=50)
    license_expiry = models.DateField(null=True, blank=True)
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
    )

    class Meta:
        db_table = 'driver_profiles'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.license_number})'
