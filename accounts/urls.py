from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .views import (
    register_pharmacy,
    staff_list,
    add_staff,
    edit_staff,
    delete_staff,
    CustomLoginView,
    logout_view,
)

urlpatterns = [
    path('register/', register_pharmacy, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),

    path(
        'password-reset/',
        PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url='/accounts/password-reset/done/'
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/accounts/reset/done/'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    path('staff/', staff_list, name='staff_list'),
    path('staff/add/', add_staff, name='add_staff'),
    path('staff/edit/<int:pk>/', edit_staff, name='edit_staff'),
    path('staff/delete/<int:pk>/', delete_staff, name='delete_staff'),
]