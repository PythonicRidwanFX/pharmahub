from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.db.models import Sum
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from drugs.models import Drug
from sales.models import Sale
from purchases.models import Purchase
from subscriptions.decorators import subscription_required
from pharmacies.decorators import pharmacy_active_required

# 🔒 Allowed roles for reports
ALLOWED_ROLES = ['owner', 'admin']


def check_access(request):
    if request.user.role not in ALLOWED_ROLES:
        raise PermissionDenied("You do not have permission to view reports.")

    if not hasattr(request.user, 'pharmacy') or request.user.pharmacy is None:
        messages.error(request, "You are not assigned to any pharmacy.")
        return None

    return request.user.pharmacy


@login_required
@subscription_required
@pharmacy_active_required
def report_home(request):
    pharmacy = check_access(request)
    if not pharmacy:
        return redirect('dashboard')

    today = now().date()
    soon = today + timedelta(days=30)

    context = {
        'pharmacy_name': pharmacy.name,
        'total_stock_items': Drug.objects.filter(pharmacy=pharmacy).count(),
        'low_stock_count': Drug.objects.filter(pharmacy=pharmacy, quantity__lt=10).count(),
        'expired_count': Drug.objects.filter(pharmacy=pharmacy, expiry_date__lt=today).count(),
        'expiring_soon_count': Drug.objects.filter(
            pharmacy=pharmacy,
            expiry_date__range=[today, soon]
        ).count(),
        'total_sales': Sale.objects.filter(pharmacy=pharmacy).aggregate(
            total=Sum('total_price')
        )['total'] or 0,
        'total_purchases': Purchase.objects.filter(pharmacy=pharmacy).aggregate(
            total=Sum('total_cost')
        )['total'] or 0,
    }

    return render(request, 'reports/report_home.html', context)


@login_required
@subscription_required
@pharmacy_active_required
def stock_report(request):
    pharmacy = check_access(request)
    if not pharmacy:
        return redirect('dashboard')

    drugs = Drug.objects.filter(pharmacy=pharmacy).order_by('drug_name')

    return render(request, 'reports/stock_report.html', {
        'pharmacy_name': pharmacy.name,
        'drugs': drugs
    })


@login_required
@subscription_required
@pharmacy_active_required
def sales_report(request):
    pharmacy = check_access(request)
    if not pharmacy:
        return redirect('dashboard')

    sales = Sale.objects.filter(pharmacy=pharmacy).select_related('drug', 'sold_by')
    total_sales = sales.aggregate(total=Sum('total_price'))['total'] or 0

    return render(request, 'reports/sales_report.html', {
        'pharmacy_name': pharmacy.name,
        'sales': sales,
        'total_sales': total_sales,
    })


@login_required
@subscription_required
@pharmacy_active_required
def purchase_report(request):
    pharmacy = check_access(request)
    if not pharmacy:
        return redirect('dashboard')

    purchases = Purchase.objects.filter(pharmacy=pharmacy).select_related('drug')
    total_purchases = purchases.aggregate(total=Sum('total_cost'))['total'] or 0

    return render(request, 'reports/purchase_report.html', {
        'pharmacy_name': pharmacy.name,
        'purchases': purchases,
        'total_purchases': total_purchases,
    })


@login_required
@subscription_required
@pharmacy_active_required
def expiry_report(request):
    pharmacy = check_access(request)
    if not pharmacy:
        return redirect('dashboard')

    today = now().date()
    soon = today + timedelta(days=30)

    expired_drugs = Drug.objects.filter(
        pharmacy=pharmacy,
        expiry_date__lt=today
    ).order_by('expiry_date')

    expiring_soon = Drug.objects.filter(
        pharmacy=pharmacy,
        expiry_date__range=[today, soon]
    ).order_by('expiry_date')

    return render(request, 'reports/expiry_report.html', {
        'pharmacy_name': pharmacy.name,
        'expired_drugs': expired_drugs,
        'expiring_soon': expiring_soon,
    })


# ================= PRINT VIEWS ================= #

@login_required
@subscription_required
@pharmacy_active_required
def print_stock_report(request):
    pharmacy = check_access(request)
    if not pharmacy:
        return redirect('dashboard')

    drugs = Drug.objects.filter(pharmacy=pharmacy).order_by('drug_name')

    return render(request, 'reports/print_stock_report.html', {
        'pharmacy_name': pharmacy.name,
        'drugs': drugs
    })


@login_required
@subscription_required
@pharmacy_active_required
def print_sales_report(request):
    pharmacy = check_access(request)
    if not pharmacy:
        return redirect('dashboard')

    sales = Sale.objects.filter(pharmacy=pharmacy).select_related('drug', 'sold_by')
    total_sales = sales.aggregate(total=Sum('total_price'))['total'] or 0

    return render(request, 'reports/print_sales_report.html', {
        'pharmacy_name': pharmacy.name,
        'sales': sales,
        'total_sales': total_sales,
    })


@login_required
@subscription_required
@pharmacy_active_required
def print_purchase_report(request):
    pharmacy = check_access(request)
    if not pharmacy:
        return redirect('dashboard')

    purchases = Purchase.objects.filter(pharmacy=pharmacy).select_related('drug')
    total_purchases = purchases.aggregate(total=Sum('total_cost'))['total'] or 0

    return render(request, 'reports/print_purchase_report.html', {
        'pharmacy_name': pharmacy.name,
        'purchases': purchases,
        'total_purchases': total_purchases,
    })


@login_required
@subscription_required
@pharmacy_active_required
def print_expiry_report(request):
    pharmacy = check_access(request)
    if not pharmacy:
        return redirect('dashboard')

    today = now().date()
    soon = today + timedelta(days=30)

    expired_drugs = Drug.objects.filter(
        pharmacy=pharmacy,
        expiry_date__lt=today
    ).order_by('expiry_date')

    expiring_soon = Drug.objects.filter(
        pharmacy=pharmacy,
        expiry_date__range=[today, soon]
    ).order_by('expiry_date')

    return render(request, 'reports/print_expiry_report.html', {
        'pharmacy_name': pharmacy.name,
        'expired_drugs': expired_drugs,
        'expiring_soon': expiring_soon,
    })