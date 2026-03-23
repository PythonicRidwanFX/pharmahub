from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from subscriptions.models import Subscription


def subscription_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user

        # 🔒 Check pharmacy
        if not hasattr(user, 'pharmacy') or user.pharmacy is None:
            messages.error(request, "You are not assigned to any pharmacy.")
            return redirect('dashboard')

        # 🔍 Get subscription
        subscription = Subscription.objects.filter(
            pharmacy=user.pharmacy,
            is_current=True
        ).first()

        # ❌ FIX: handle None
        if subscription is None:
            messages.error(request, "No subscription found. Please choose a plan.")
            return redirect('plan_list')

        today = timezone.now().date()

        # ✅ Allow trial + active
        if subscription.status in ['trial', 'active']:
            if not subscription.end_date or subscription.end_date >= today:
                return view_func(request, *args, **kwargs)

        # ❌ Expired or inactive
        messages.error(request, "Your subscription is inactive or expired. Please renew to continue.")
        return redirect('plan_list')

    return wrapper