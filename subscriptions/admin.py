from django.contrib import admin
from .models import Plan, Subscription, Payment


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'billing_cycle', 'duration_days', 'max_staff', 'is_active')
    list_filter = ('billing_cycle', 'is_active')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'plan', 'status', 'start_date', 'end_date', 'is_current')
    list_filter = ('status', 'is_current')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'plan', 'amount', 'reference', 'status', 'payment_gateway', 'paid_at')
    list_filter = ('status', 'payment_gateway')
    search_fields = ('reference', 'email', 'pharmacy__name')