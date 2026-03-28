from django.db import models
from django.utils import timezone
from pharmacies.models import Pharmacy


class Plan(models.Model):
    BILLING_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CHOICES, default='monthly')
    duration_days = models.PositiveIntegerField(default=30)
    max_staff = models.PositiveIntegerField(default=3)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - ₦{self.price}"


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    )

    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=True)

    def __str__(self):
        plan_name = self.plan.name if self.plan else "No Plan"
        return f"{self.pharmacy.name} - {plan_name} - {self.status}"

    @property
    def is_active_subscription(self):
        today = timezone.now().date()
        return self.status in ['trial', 'active'] and self.end_date >= today

    @property
    def days_left(self):
        return (self.end_date - timezone.now().date()).days


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=255, unique=True)
    email = models.EmailField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_gateway = models.CharField(max_length=50, default='flutterwave')

    access_code = models.CharField(max_length=255, blank=True, null=True)
    gateway_response = models.CharField(max_length=255, blank=True, null=True)

    flutterwave_tx_id = models.CharField(max_length=255, blank=True, null=True)
    flutterwave_tx_ref = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=10, default='NGN')
    payment_link = models.URLField(blank=True, null=True)

    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pharmacy.name} - {self.reference} - {self.status}"