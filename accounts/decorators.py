from django.core.exceptions import PermissionDenied


def admin_required(user):
    return user.is_authenticated and user.role in ['owner', 'admin']