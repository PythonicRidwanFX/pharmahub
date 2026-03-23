from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Sale
from .forms import SaleForm
from subscriptions.decorators import subscription_required
from pharmacies.decorators import pharmacy_active_required


@login_required
@subscription_required
@pharmacy_active_required
def sale_list(request):
    # 🔒 Ensure user has a pharmacy
    if not hasattr(request.user, 'pharmacy') or request.user.pharmacy is None:
        messages.error(request, "You are not assigned to any pharmacy.")
        return redirect('dashboard')

    sales = Sale.objects.filter(
        pharmacy=request.user.pharmacy
    ).select_related('drug', 'sold_by')

    return render(request, 'sales/sale_list.html', {'sales': sales})


@login_required
@subscription_required
@pharmacy_active_required
def add_sale(request):
    # 🔒 Role restriction
    if request.user.role not in ['owner', 'admin', 'cashier', 'pharmacist']:
        raise PermissionDenied("You do not have permission to record sales.")

    # 🔒 Ensure user has a pharmacy
    if not hasattr(request.user, 'pharmacy') or request.user.pharmacy is None:
        messages.error(request, "You are not assigned to any pharmacy.")
        return redirect('dashboard')

    pharmacy = request.user.pharmacy

    if request.method == 'POST':
        form = SaleForm(request.POST, pharmacy=pharmacy)

        if form.is_valid():
            sale = form.save(commit=False)
            sale.pharmacy = pharmacy
            sale.sold_by = request.user

            drug = sale.drug

            # 🔴 Stock check
            if sale.quantity > drug.quantity:
                messages.error(request, 'Not enough stock available for this sale.')
            else:
                # ✅ Save sale
                sale.save()

                # ✅ Update stock
                drug.quantity -= sale.quantity
                drug.save()

                messages.success(request, 'Sale recorded successfully and stock updated.')
                return redirect('sale_list')
        else:
            messages.error(request, "Please correct the form errors.")

    else:
        form = SaleForm(pharmacy=pharmacy)

    return render(request, 'sales/add_sale.html', {'form': form})