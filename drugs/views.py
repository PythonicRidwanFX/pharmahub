from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Drug
from .forms import DrugForm
from subscriptions.decorators import subscription_required
from pharmacies.decorators import pharmacy_active_required


@login_required
@subscription_required
@pharmacy_active_required
def drug_list(request):
    drugs = Drug.objects.filter(pharmacy=request.user.pharmacy)
    return render(request, 'drugs/drug_list.html', {'drugs': drugs})


@login_required
@subscription_required
@pharmacy_active_required
def add_drug(request):
    if request.method == 'POST':
        form = DrugForm(request.POST)
        if form.is_valid():
            drug = form.save(commit=False)
            drug.pharmacy = request.user.pharmacy
            drug.save()
            return redirect('drug_list')
    else:
        form = DrugForm()

    return render(request, 'drugs/add_drug.html', {'form': form})


@login_required
@subscription_required
@pharmacy_active_required
def edit_drug(request, pk):
    drug = get_object_or_404(Drug, pk=pk, pharmacy=request.user.pharmacy)

    if request.method == 'POST':
        form = DrugForm(request.POST, instance=drug)
        if form.is_valid():
            form.save()
            return redirect('drug_list')
    else:
        form = DrugForm(instance=drug)

    return render(request, 'drugs/edit_drug.html', {'form': form, 'drug': drug})


@login_required
@subscription_required
@pharmacy_active_required
def expiry_alerts(request):
    today = now().date()
    soon = today + timedelta(days=30)

    expired_drugs = Drug.objects.filter(
        pharmacy=request.user.pharmacy,
        expiry_date__lt=today
    )

    expiring_soon = Drug.objects.filter(
        pharmacy=request.user.pharmacy,
        expiry_date__range=[today, soon]
    )

    context = {
        'expired_drugs': expired_drugs,
        'expiring_soon': expiring_soon,
    }
    return render(request, 'drugs/expiry_alerts.html', context)


@login_required
@subscription_required
@pharmacy_active_required
def low_stock(request):
    low_stock_drugs = Drug.objects.filter(
        pharmacy=request.user.pharmacy,
        quantity__lt=10
    )
    return render(request, 'drugs/low_stock.html', {'low_stock_drugs': low_stock_drugs})