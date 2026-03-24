from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


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


class StaffCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']



from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username or email',
            'autocomplete': 'username',
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'current-password',
        })
    )

    def confirm_login_allowed(self, user):
        """
        Extra security check (very professional)
        """
        if not user.is_active:
            raise forms.ValidationError(
                "This account is inactive. Please contact support.",
                code='inactive',
            )