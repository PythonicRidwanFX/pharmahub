from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


# ===============================
# PHARMACY REGISTRATION FORM
# ===============================
class PharmacyRegistrationForm(UserCreationForm):
    pharmacy_name = forms.CharField(max_length=255)
    pharmacy_email = forms.EmailField()
    pharmacy_phone = forms.CharField(max_length=20, required=False)
    pharmacy_address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'pharmacy_name',
            'pharmacy_email',
            'pharmacy_phone',
            'pharmacy_address',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add basic styling (important)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# ===============================
# STAFF CREATE FORM
# ===============================
class StaffCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# ===============================
# LOGIN FORM (USERNAME OR EMAIL)
# ===============================
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username or email',
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
        })
    )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "This account is inactive. Please contact support.",
                code='inactive',
            )