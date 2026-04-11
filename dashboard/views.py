from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.db.models import Sum

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
    pharmacy = request.user.pharmacy
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

    recent_drugs = Drug.objects.filter(
        pharmacy=pharmacy
    ).order_by('-created_at')[:5]

    today_sales = Sale.objects.filter(
        pharmacy=pharmacy,
        date__date=today
    ).aggregate(total=Sum('total_price'))['total'] or 0

    today_purchases = Purchase.objects.filter(
        pharmacy=pharmacy,
        date__date=today
    ).aggregate(total=Sum('total_cost'))['total'] or 0

    recent_sales = Sale.objects.filter(
        pharmacy=pharmacy
    ).select_related('drug').order_by('-date')[:5]

    recent_purchases = Purchase.objects.filter(
        pharmacy=pharmacy
    ).select_related('drug').order_by('-date')[:5]

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

    context = {
        'testimonials': testimonials,
        'form': form,
    }

    return render(request, 'landing.html', context)