from django.core.management.base import BaseCommand
from subscriptions.reminders import send_expiry_reminders, send_expired_notifications
from subscriptions.expiry import expire_subscriptions_and_suspend


class Command(BaseCommand):
    help = "Send subscription reminders and expire overdue subscriptions"

    def handle(self, *args, **options):
        expired_count = expire_subscriptions_and_suspend()
        reminder_count = send_expiry_reminders()
        expired_notice_count = send_expired_notifications()

        self.stdout.write(
            self.style.SUCCESS(
                f"Subscriptions expired: {expired_count}, "
                f"reminders sent: {reminder_count}, "
                f"expired notices sent: {expired_notice_count}"
            )
        )