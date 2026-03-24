def admin_required(user):
    if not user.is_authenticated:
        return False
    return user.role in ['owner', 'pharmacist']


def owner_required(user):
    if not user.is_authenticated:
        return False
    return user.role == 'owner'


def role_required(allowed_roles):
    def check_role(user):
        if not user.is_authenticated:
            return False

        if user.role == 'owner':
            return True

        return user.role in allowed_roles

    return check_role