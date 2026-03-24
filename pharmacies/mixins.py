from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class PharmacyAccessMixin(LoginRequiredMixin):
    def get_pharmacy(self):
        pharmacy = getattr(self.request.user, 'pharmacy', None)
        if not pharmacy:
            raise PermissionDenied("No pharmacy linked to this user.")
        return pharmacy