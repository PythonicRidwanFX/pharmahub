from django.contrib import admin
from .models import Drug


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('drug_name', 'pharmacy', 'quantity', 'unit_price', 'expiry_date')
    search_fields = ('drug_name', 'category', 'manufacturer')
    list_filter = ('pharmacy', 'expiry_date')