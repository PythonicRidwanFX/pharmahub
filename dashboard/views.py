from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Sum
from drugs.models import Drug
from sales.models import Sale
from purchases.models import Purchase
from subscriptions.decorators import subscription_required
from pharmacies.decorators import pharmacy_active_required

@login_required
@pharmacy_active_required
@subscription_required
def dashboard_view(request):
    pharmacy = request.user.pharmacy
    today = now().date()
    soon = today + timedelta(days=30)

    # Stock counts
    total_drugs = Drug.objects.filter(pharmacy=pharmacy).count()
    expired_count = Drug.objects.filter(
        pharmacy=pharmacy,
        expiry_date__lt=today
    ).count()
    expiring_soon_count = Drug.objects.filter(
        pharmacy=pharmacy,
        expiry_date__range=[today, soon]
    ).count()
    low_stock_count = Drug.objects.filter(
        pharmacy=pharmacy,
        quantity__lt=10
    ).count()

    # Recent entries
    recent_drugs = Drug.objects.filter(pharmacy=pharmacy).order_by('-created_at')[:5]

    # Today's sales and purchases
    today_sales = Sale.objects.filter(
        pharmacy=pharmacy,
        date__date=today
    ).aggregate(total=Sum('total_price'))['total'] or 0

    today_purchases = Purchase.objects.filter(
        pharmacy=pharmacy,
        date__date=today
    ).aggregate(total=Sum('total_cost'))['total'] or 0

    # Recent sales and purchases
    recent_sales = Sale.objects.filter(pharmacy=pharmacy).select_related('drug')[:5]
    recent_purchases = Purchase.objects.filter(pharmacy=pharmacy).select_related('drug')[:5]

    context = {
        'total_drugs': total_drugs,
        'expired_count': expired_count,
        'expiring_soon_count': expiring_soon_count,
        'low_stock_count': low_stock_count,
        'recent_drugs': recent_drugs,
        'today_sales': today_sales,
        'today_purchases': today_purchases,
        'recent_sales': recent_sales,
        'recent_purchases': recent_purchases,
    }

    return render(request, 'dashboard/index.html', context)



def help_view(request):
    return render(request, 'help.html')