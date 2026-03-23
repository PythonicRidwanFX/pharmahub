from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Pharmacy Info', {'fields': ('pharmacy', 'role')}),
    )

    list_display = ('username', 'email', 'role', 'pharmacy', 'is_staff', 'is_active')
    list_filter = ('role', 'pharmacy')