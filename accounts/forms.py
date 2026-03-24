from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from pharmacies.models import Pharmacy


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

    def clean_pharmacy_email(self):
        pharmacy_email = self.cleaned_data.get('pharmacy_email')
        if Pharmacy.objects.filter(email__iexact=pharmacy_email).exists():
            raise forms.ValidationError('A pharmacy with this email already exists.')
        return pharmacy_email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email


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