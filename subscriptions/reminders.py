from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone

from .models import Subscription


def send_expiry_reminders():
    today = timezone.now().date()

    target_days = [7, 3, 1]

    subscriptions = Subscription.objects.select_related("pharmacy", "plan").filter(
        is_current=True,
        status__in=["trial", "active"],
        end_date__gte=today
    )

    sent_count = 0

    for subscription in subscriptions:
        days_left = (subscription.end_date - today).days

        if days_left in target_days:
            pharmacy = subscription.pharmacy
            plan_name = subscription.plan.name if subscription.plan else "Trial"

            subject = f"Your PharmaHub subscription expires in {days_left} day(s)"
            message = (
                f"Hello {pharmacy.name},\n\n"
                f"Your {plan_name} subscription will expire in {days_left} day(s), "
                f"on {subscription.end_date}.\n\n"
                f"Please renew your subscription to avoid interruption.\n\n"
                f"Regards,\n"
                f"PharmaHub"
            )

            if pharmacy.email:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,
                    recipient_list=[pharmacy.email],
                    fail_silently=False,
                )
                sent_count += 1

    return sent_count


def send_expired_notifications():
    today = timezone.now().date()

    subscriptions = Subscription.objects.select_related("pharmacy", "plan").filter(
        is_current=True,
        status__in=["trial", "active"],
        end_date__lt=today
    )

    sent_count = 0

    for subscription in subscriptions:
        pharmacy = subscription.pharmacy
        plan_name = subscription.plan.name if subscription.plan else "Trial"

        if pharmacy.email:
            send_mail(
                subject="Your PharmaHub subscription has expired",
                message=(
                    f"Hello {pharmacy.name},\n\n"
                    f"Your {plan_name} subscription expired on {subscription.end_date}.\n"
                    f"Please renew to continue using PharmaHub.\n\n"
                    f"Regards,\nPharmaHub"
                ),
                from_email=None,
                recipient_list=[pharmacy.email],
                fail_silently=False,
            )
            sent_count += 1

        subscription.status = "expired"
        subscription.save(update_fields=["status"])

    return sent_count