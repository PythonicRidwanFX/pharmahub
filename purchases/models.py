from django.db import models
from pharmacies.models import Pharmacy
from drugs.models import Drug


class Purchase(models.Model):
    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    supplier = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.drug.drug_name} - {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.purchase_price
        super().save(*args, **kwargs)