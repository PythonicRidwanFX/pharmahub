from django.core.exceptions import PermissionDenied


def admin_required(user):
    if not user.is_authenticated:
        return False

    # ✅ Owner OR Pharmacist can manage system
    if user.is_owner or user.role == 'pharmacist':
        return True

    return False


def owner_required(user):
    if not user.is_authenticated:
        return False

    return user.is_owner


def role_required(allowed_roles):
    def decorator(user):
        if not user.is_authenticated:
            return False

        if user.is_owner:
            return True  # owner has full access

        if user.role in allowed_roles:
            return True

        return False

    return decorator