from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()


def superadmin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        superadmin_id = request.session.get('superadmin_id')

        if not superadmin_id:
            messages.error(request, 'Please log in as superadmin.')
            return redirect('superadmin_login')

        try:
            superadmin_user = User.objects.get(id=superadmin_id, is_superuser=True)
        except User.DoesNotExist:
            request.session.pop('superadmin_id', None)
            messages.error(request, 'Superadmin session is invalid. Please log in again.')
            return redirect('superadmin_login')

        request.superadmin_user = superadmin_user
        return view_func(request, *args, **kwargs)

    return wrapper