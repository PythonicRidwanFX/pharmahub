from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import User
from django.shortcuts import redirect
from django.contrib import messages
from pharmacies.models import Pharmacy
from .decorators import admin_required
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from subscriptions.access import sync_pharmacy_access
from .forms import PharmacyRegistrationForm, StaffCreateForm, CustomLoginForm

from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import PharmacyRegistrationForm
from subscriptions.models import Subscription


def register_pharmacy(request):
    if request.method == 'POST':
        form = PharmacyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            today = timezone.now().date()
            Subscription.objects.create(
                pharmacy=user.pharmacy,
                plan=None,
                status='trial',
                start_date=today,
                end_date=today + timezone.timedelta(days=14),
                is_current=True
            )

            login(request, user)
            messages.success(
                request,
                'Account created successfully. Your 14-day trial has started.'
            )
            return redirect('dashboard')
    else:
        form = PharmacyRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})
@login_required
@user_passes_test(admin_required)
def staff_list(request):
    staff_members = User.objects.filter(
        pharmacy=request.user.pharmacy
    ).order_by('username')

    return render(request, 'accounts/staff_list.html', {
        'staff_members': staff_members
    })


from subscriptions.models import Subscription

@login_required
@user_passes_test(admin_required)
def add_staff(request):
    current_subscription = Subscription.objects.filter(
        pharmacy=request.user.pharmacy,
        is_current=True,
        status__in=['trial', 'active']
    ).first()

    if current_subscription and current_subscription.plan:
        current_staff_count = User.objects.filter(pharmacy=request.user.pharmacy).count()
        if current_staff_count >= current_subscription.plan.max_staff:
            messages.error(request, 'You have reached the maximum staff limit for your plan.')
            return redirect('staff_list')

    if request.method == 'POST':
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.pharmacy = request.user.pharmacy
            staff.save()
            messages.success(request, 'Staff account created successfully.')
            return redirect('staff_list')
    else:
        form = StaffCreateForm()

    return render(request, 'accounts/add_staff.html', {'form': form})

@login_required
@user_passes_test(admin_required)
def edit_staff(request, pk):
    staff = get_object_or_404(
        User,
        pk=pk,
        pharmacy=request.user.pharmacy
    )

    if request.method == 'POST':
        staff.username = request.POST.get('username')
        staff.email = request.POST.get('email')
        staff.role = request.POST.get('role')
        staff.save()
        messages.success(request, 'Staff updated successfully.')
        return redirect('staff_list')

    return render(request, 'accounts/edit_staff.html', {'staff': staff})


@login_required
@user_passes_test(admin_required)
def delete_staff(request, pk):
    staff = get_object_or_404(
        User,
        pk=pk,
        pharmacy=request.user.pharmacy
    )

    if staff.role == 'owner':
        messages.error(request, 'Owner account cannot be deleted.')
        return redirect('staff_list')

    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff deleted successfully.')
        return redirect('staff_list')

    return render(request, 'accounts/delete_staff.html', {'staff': staff})



class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        if user.is_superuser:
            return redirect('admin_dashboard')

        pharmacy = getattr(user, 'pharmacy', None)

        if not pharmacy:
            logout(self.request)
            messages.error(self.request, 'No pharmacy account is linked to this user.')
            return redirect('login')

        sync_pharmacy_access(pharmacy)
        pharmacy.refresh_from_db()

        if pharmacy.is_suspended_by_owner:
            logout(self.request)
            messages.error(
                self.request,
                'Your pharmacy account has been suspended by the platform owner. Please contact support.'
            )
            return redirect('login')

        if not pharmacy.is_active:
            messages.warning(
                self.request,
                'Your subscription is inactive or expired. Please renew to continue.'
            )
            return redirect('plan_list')

        return redirect('dashboard')



from django.views.decorators.http import require_POST

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')