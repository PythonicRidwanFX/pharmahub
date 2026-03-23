from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count
from django.utils import timezone
from django.db.models.functions import TruncMonth
import json

from pharmacies.models import Pharmacy
from accounts.models import User
from drugs.models import Drug
from subscriptions.models import Subscription, Payment, Plan

from superadmin_panel.decorators import superadmin_required
from django.contrib import messages
from django.http import HttpResponse


# ================= DASHBOARD ================= #

@superadmin_required
def admin_dashboard(request):
    today = timezone.now().date()

    total_pharmacies = Pharmacy.objects.count()
    total_users = User.objects.count()
    total_drugs = Drug.objects.count()

    active_subscriptions = Subscription.objects.filter(
        status__in=['trial', 'active'],
        end_date__gte=today,
        is_current=True
    ).count()

    expired_subscriptions = Subscription.objects.filter(
        end_date__lt=today,
        is_current=True
    ).count()

    total_revenue = Payment.objects.filter(
        status='success'
    ).aggregate(total=Sum('amount'))['total'] or 0

    successful_payments = Payment.objects.filter(status='success').count()
    pending_payments = Payment.objects.filter(status='pending').count()
    failed_payments = Payment.objects.filter(status='failed').count()

    recent_pharmacies = Pharmacy.objects.order_by('-created_at')[:5]
    recent_payments = Payment.objects.select_related('pharmacy', 'plan').order_by('-created_at')[:10]
    recent_subscriptions = Subscription.objects.select_related('pharmacy', 'plan').order_by('-id')[:10]

    monthly_revenue_qs = (
        Payment.objects.filter(status='success')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    pharmacy_growth_qs = (
        Pharmacy.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    revenue_labels = [item['month'].strftime('%b %Y') for item in monthly_revenue_qs if item['month']]
    revenue_values = [float(item['total']) for item in monthly_revenue_qs]

    pharmacy_labels = [item['month'].strftime('%b %Y') for item in pharmacy_growth_qs if item['month']]
    pharmacy_values = [item['total'] for item in pharmacy_growth_qs]

    subscription_status_labels = ['Active/Trial', 'Expired']
    subscription_status_values = [active_subscriptions, expired_subscriptions]

    payment_status_labels = ['Success', 'Pending', 'Failed']
    payment_status_values = [successful_payments, pending_payments, failed_payments]

    context = {
        'total_pharmacies': total_pharmacies,
        'total_users': total_users,
        'total_drugs': total_drugs,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'total_revenue': total_revenue,
        'successful_payments': successful_payments,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'recent_pharmacies': recent_pharmacies,
        'recent_payments': recent_payments,
        'recent_subscriptions': recent_subscriptions,

        'revenue_labels': json.dumps(revenue_labels),
        'revenue_values': json.dumps(revenue_values),
        'pharmacy_labels': json.dumps(pharmacy_labels),
        'pharmacy_values': json.dumps(pharmacy_values),
        'subscription_status_labels': json.dumps(subscription_status_labels),
        'subscription_status_values': json.dumps(subscription_status_values),
        'payment_status_labels': json.dumps(payment_status_labels),
        'payment_status_values': json.dumps(payment_status_values),
    }
    return render(request, 'superadmin_panel/dashboard.html', context)


# ================= PHARMACY ================= #

@superadmin_required
def pharmacy_list(request):
    pharmacies = Pharmacy.objects.all().order_by('-created_at')
    return render(request, 'superadmin_panel/pharmacy_list.html', {'pharmacies': pharmacies})


@superadmin_required
def pharmacy_detail(request, pk):
    pharmacy = get_object_or_404(Pharmacy, pk=pk)
    users = User.objects.filter(pharmacy=pharmacy)
    drugs = Drug.objects.filter(pharmacy=pharmacy)
    subscriptions = Subscription.objects.filter(pharmacy=pharmacy).select_related('plan').order_by('-id')
    payments = Payment.objects.filter(pharmacy=pharmacy).select_related('plan').order_by('-created_at')

    total_revenue = payments.filter(status='success').aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'pharmacy': pharmacy,
        'users': users,
        'drugs': drugs,
        'subscriptions': subscriptions,
        'payments': payments,
        'total_revenue': total_revenue,
    }
    return render(request, 'superadmin_panel/pharmacy_detail.html', context)


# ================= PAYMENTS ================= #

@superadmin_required
def payment_list(request):
    payments = Payment.objects.select_related('pharmacy', 'plan').order_by('-created_at')
    total_revenue = payments.filter(status='success').aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'superadmin_panel/payment_list.html', {
        'payments': payments,
        'total_revenue': total_revenue,
    })


# ================= SUBSCRIPTIONS ================= #

@superadmin_required
def subscription_list(request):
    subscriptions = Subscription.objects.select_related('pharmacy', 'plan').order_by('-id')
    return render(request, 'superadmin_panel/subscription_list.html', {
        'subscriptions': subscriptions
    })


@superadmin_required
def plan_list_admin(request):
    plans = Plan.objects.all().order_by('price')
    return render(request, 'superadmin_panel/plan_list.html', {'plans': plans})


# ================= SUSPEND / ACTIVATE ================= #

@superadmin_required
def suspend_pharmacy(request, pk):
    pharmacy = get_object_or_404(Pharmacy, pk=pk)

    if request.method == 'POST':
        pharmacy.is_active = False
        pharmacy.is_suspended_by_owner = True
        pharmacy.suspension_reason = "Suspended by platform owner"
        pharmacy.save(update_fields=['is_active', 'is_suspended_by_owner', 'suspension_reason'])

        messages.success(request, f'{pharmacy.name} has been suspended.')
        return redirect('admin_pharmacy_detail', pk=pharmacy.pk)

    return render(request, 'superadmin_panel/suspend_pharmacy.html', {'pharmacy': pharmacy})


from subscriptions.access import sync_pharmacy_access

@superadmin_required
def activate_pharmacy(request, pk):
    pharmacy = get_object_or_404(Pharmacy, pk=pk)

    if request.method == 'POST':
        pharmacy.is_suspended_by_owner = False
        pharmacy.suspension_reason = ""
        pharmacy.save(update_fields=['is_suspended_by_owner', 'suspension_reason'])

        sync_pharmacy_access(pharmacy)

        messages.success(request, f'{pharmacy.name} has been activated.')
        return redirect('admin_pharmacy_detail', pk=pharmacy.pk)

    return render(request, 'superadmin_panel/activate_pharmacy.html', {'pharmacy': pharmacy})


