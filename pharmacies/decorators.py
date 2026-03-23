from django.shortcuts import redirect
from django.contrib import messages


def pharmacy_active_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not hasattr(user, 'pharmacy') or user.pharmacy is None:
            messages.error(request, "You are not assigned to any pharmacy.")
            return redirect('dashboard')

        pharmacy = user.pharmacy

        # ❌ Block ONLY if suspended by owner
        if pharmacy.is_suspended_by_owner:
            messages.error(request, "Your pharmacy account has been suspended. Please contact support.")
            return redirect('dashboard')

        # ❌ DO NOT block trial users here
        # Remove any check like:
        # if not pharmacy.is_active: ❌

        return view_func(request, *args, **kwargs)

    return wrapper