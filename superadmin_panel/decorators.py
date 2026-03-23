from django.shortcuts import redirect
from django.contrib import messages

def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):

        # ❌ Not logged in → go to login page
        if not request.user.is_authenticated:
            return redirect('login')

        # ❌ Logged in but not superadmin → block nicely
        if not request.user.is_superuser:
            messages.error(request, "You do not have permission to access this page.")
            return redirect('dashboard')  # send normal users to their dashboard

        # ✅ Superadmin → allow access
        return view_func(request, *args, **kwargs)

    return wrapper