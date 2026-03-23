from django.utils import timezone
from .models import Subscription
from .access import sync_pharmacy_access


def expire_subscriptions_and_suspend():
    today = timezone.now().date()

    expired = Subscription.objects.filter(
        is_current=True,
        status__in=["trial", "active"],
        end_date__lt=today
    ).select_related("pharmacy")

    updated = 0

    for subscription in expired:
        subscription.status = "expired"
        subscription.save(update_fields=["status"])

        sync_pharmacy_access(subscription.pharmacy)
        updated += 1

    return updated