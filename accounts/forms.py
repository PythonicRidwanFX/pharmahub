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
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
    }))