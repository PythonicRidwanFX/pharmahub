from django.core.exceptions import PermissionDenied


def role_required(user, allowed_roles):
    if not user.is_authenticated or user.role not in allowed_roles:
        raise PermissionDenied("You do not have permission to access this page.")