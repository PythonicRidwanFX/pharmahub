from django.db import models
from pharmacies.models import Pharmacy


class Drug(models.Model):
    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name='drugs'
    )
    drug_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, null=True)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    expiry_date = models.DateField()
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['drug_name']

    def __str__(self):
        return self.drug_name

    @property
    def is_low_stock(self):
        return self.quantity < 10