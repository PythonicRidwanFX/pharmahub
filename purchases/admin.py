from django.contrib import admin
from .models import Purchase


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('drug', 'pharmacy', 'supplier', 'quantity', 'purchase_price', 'total_cost', 'date')
    list_filter = ('pharmacy', 'date')
    search_fields = ('drug__drug_name', 'supplier')