from django.contrib import admin
from .models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('drug', 'pharmacy', 'sold_by', 'quantity', 'unit_price', 'total_price', 'date')
    list_filter = ('pharmacy', 'date')
    search_fields = ('drug__drug_name', 'customer_name')