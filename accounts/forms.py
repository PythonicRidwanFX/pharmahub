from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
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
    role = forms.ChoiceField(
        choices=[
            ('admin', 'Admin'),
            ('pharmacist', 'Pharmacist'),
            ('cashier', 'Cashier'),
            ('staff', 'Staff'),
        ]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter username or email',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter password',
        })
    )