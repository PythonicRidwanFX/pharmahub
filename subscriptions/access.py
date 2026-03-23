from django.utils import timezone
from subscriptions.models import Subscription


def sync_pharmacy_access(pharmacy):
    """
    Decide whether a pharmacy should currently have access.
    Manual owner suspension always wins.
    Otherwise, current valid subscription controls access.
    """
    if pharmacy.is_suspended_by_owner:
        pharmacy.is_active = False
        pharmacy.save(update_fields=["is_active"])
        return False

    today = timezone.now().date()

    current_subscription = Subscription.objects.filter(
        pharmacy=pharmacy,
        is_current=True,
        status__in=["trial", "active"],
        end_date__gte=today
    ).first()

    should_be_active = current_subscription is not None

    if pharmacy.is_active != should_be_active:
        pharmacy.is_active = should_be_active
        pharmacy.save(update_fields=["is_active"])

    return should_be_active