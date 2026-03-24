from django.contrib.auth.models import AbstractUser
from django.db import models
from pharmacies.models import Pharmacy


class User(AbstractUser):
    ROLE_CHOICES = (
        ('pharmacist', 'Pharmacist'),
        ('cashier', 'Cashier'),
        ('staff', 'Staff'),
    )

    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff'
    )

    def __str__(self):
        return f"{self.username} - {self.role}"

    @property
    def is_owner(self):
        return self.pharmacy is not None and self.pharmacy.owner == self

    @property
    def is_admin_user(self):
        return self.is_owner or self.role == 'pharmacist'