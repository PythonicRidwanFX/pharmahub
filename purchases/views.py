from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import Purchase
from .forms import PurchaseForm
from subscriptions.decorators import subscription_required
from pharmacies.decorators import pharmacy_active_required


@login_required
@subscription_required
@pharmacy_active_required
def purchase_list(request):
    if not hasattr(request.user, 'pharmacy') or request.user.pharmacy is None:
        messages.error(request, "You are not assigned to any pharmacy.")
        return redirect('dashboard')

    purchases = Purchase.objects.filter(
        pharmacy=request.user.pharmacy
    ).select_related('drug')

    return render(request, 'purchases/purchase_list.html', {'purchases': purchases})


@login_required
@subscription_required
@pharmacy_active_required
def add_purchase(request):
    if request.user.role not in ['owner', 'admin', 'pharmacist', 'staff', 'cashier']:
        raise PermissionDenied("You do not have permission to add purchases.")

    if not hasattr(request.user, 'pharmacy') or request.user.pharmacy is None:
        messages.error(request, "You are not assigned to any pharmacy.")
        return redirect('dashboard')

    pharmacy = request.user.pharmacy

    if request.method == 'POST':
        form = PurchaseForm(request.POST, pharmacy=pharmacy)

        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.pharmacy = pharmacy
            purchase.save()

            drug = purchase.drug
            drug.quantity += purchase.quantity
            drug.save()

            messages.success(request, 'Purchase recorded successfully and stock updated.')
            return redirect('purchase_list')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = PurchaseForm(pharmacy=pharmacy)

    return render(request, 'purchases/add_purchase.html', {'form': form})