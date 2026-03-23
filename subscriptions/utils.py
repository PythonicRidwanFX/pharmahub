from django.utils import timezone
from .models import Subscription
from .access import sync_pharmacy_access


def deactivate_old_subscriptions(pharmacy):
    Subscription.objects.filter(
        pharmacy=pharmacy,
        is_current=True
    ).update(is_current=False)


def create_subscription(pharmacy, plan, status='active'):
    deactivate_old_subscriptions(pharmacy)

    today = timezone.now().date()
    end_date = today + timezone.timedelta(days=plan.duration_days)

    subscription = Subscription.objects.create(
        pharmacy=pharmacy,
        plan=plan,
        status=status,
        start_date=today,
        end_date=end_date,
        is_current=True
    )

    sync_pharmacy_access(pharmacy)
    return subscription