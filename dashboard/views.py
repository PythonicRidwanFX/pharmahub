from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.db.models import Sum
from django.db.models.functions import TruncDate

from drugs.models import Drug
from sales.models import Sale
from purchases.models import Purchase
from subscriptions.decorators import subscription_required
from pharmacies.decorators import pharmacy_active_required
from .models import Testimonial
from .forms import TestimonialForm


@login_required
@pharmacy_active_required
@subscription_required
def dashboard_view(request):
    pharmacy = getattr(request.user, 'pharmacy', None)

    if pharmacy is None:
        context = {
            'total_drugs': 0,
            'expired_count': 0,
            'expiring_soon_count': 0,
            'low_stock_count': 0,
            'today_sales': Decimal('0.00'),
            'today_purchases': Decimal('0.00'),
            'recent_drugs': [],
            'recent_sales': [],
            'recent_purchases': [],
            'chart_labels': [],
            'sales_chart_data': [],
            'purchases_chart_data': [],
            'inventory_chart_data': [0, 0, 0, 0],
            'best_sales_day': "No data yet",
            'top_selling_drug': "No sales yet",
            'inventory_analysis': "No pharmacy assigned to this account",
        }
        return render(request, 'dashboard/dashboard.html', context)

    today = now().date()
    soon = today + timedelta(days=30)

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

    healthy_stock_count = Drug.objects.filter(
        pharmacy=pharmacy,
        quantity__gte=10,
        expiry_date__gt=soon
    ).count()

    today_sales = Sale.objects.filter(
        pharmacy=pharmacy,
        date__date=today
    ).aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')

    today_purchases = Purchase.objects.filter(
        pharmacy=pharmacy,
        date__date=today
    ).aggregate(total=Sum('total_cost'))['total'] or Decimal('0.00')

    recent_drugs = Drug.objects.filter(
        pharmacy=pharmacy
    ).order_by('-id')[:5]

    recent_sales = Sale.objects.filter(
        pharmacy=pharmacy
    ).select_related('drug').order_by('-date')[:5]

    recent_purchases = Purchase.objects.filter(
        pharmacy=pharmacy
    ).select_related('drug').order_by('-date')[:5]

    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    chart_labels = [day.strftime('%a') for day in last_7_days]

    sales_summary = Sale.objects.filter(
        pharmacy=pharmacy,
        date__date__gte=last_7_days[0],
        date__date__lte=today
    ).annotate(day=TruncDate('date')).values('day').annotate(
        total=Sum('total_price')
    ).order_by('day')

    purchases_summary = Purchase.objects.filter(
        pharmacy=pharmacy,
        date__date__gte=last_7_days[0],
        date__date__lte=today
    ).annotate(day=TruncDate('date')).values('day').annotate(
        total=Sum('total_cost')
    ).order_by('day')

    sales_map = {item['day']: float(item['total'] or 0) for item in sales_summary}
    purchases_map = {item['day']: float(item['total'] or 0) for item in purchases_summary}

    sales_chart_data = [sales_map.get(day, 0) for day in last_7_days]
    purchases_chart_data = [purchases_map.get(day, 0) for day in last_7_days]

    inventory_chart_data = [
        healthy_stock_count,
        low_stock_count,
        expiring_soon_count,
        expired_count,
    ]

    best_sales_day = "No data yet"
    sales_summary_list = list(sales_summary)

    if sales_summary_list:
        best_day_entry = max(sales_summary_list, key=lambda x: x['total'] or 0)
        if best_day_entry['day']:
            best_sales_day = best_day_entry['day'].strftime('%A')

    top_selling = Sale.objects.filter(
        pharmacy=pharmacy
    ).values('drug__drug_name').annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty').first()

    top_selling_drug = top_selling['drug__drug_name'] if top_selling else "No sales yet"

    if expired_count > 0:
        inventory_analysis = "Some drugs need urgent attention"
    elif low_stock_count > 0 or expiring_soon_count > 0:
        inventory_analysis = "Stock is stable but needs monitoring"
    else:
        inventory_analysis = "Inventory is in healthy condition"

    context = {
        'total_drugs': total_drugs,
        'expired_count': expired_count,
        'expiring_soon_count': expiring_soon_count,
        'low_stock_count': low_stock_count,
        'today_sales': today_sales,
        'today_purchases': today_purchases,
        'recent_drugs': recent_drugs,
        'recent_sales': recent_sales,
        'recent_purchases': recent_purchases,
        'chart_labels': chart_labels,
        'sales_chart_data': sales_chart_data,
        'purchases_chart_data': purchases_chart_data,
        'inventory_chart_data': inventory_chart_data,
        'best_sales_day': best_sales_day,
        'top_selling_drug': top_selling_drug,
        'inventory_analysis': inventory_analysis,
    }

    return render(request, 'dashboard/index.html', context)


@login_required
@pharmacy_active_required
@subscription_required
def help_view(request):
    return render(request, 'dashboard/help.html')


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    testimonials = Testimonial.objects.all().order_by('-created_at')

    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('landing_page')
    else:
        form = TestimonialForm()

    return render(request, 'landing.html', {
        'testimonials': testimonials,
        'form': form,
    })