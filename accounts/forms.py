from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from pharmacies.models import Pharmacy


class PharmacyRegistrationForm(UserCreationForm):
    pharmacy_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    pharmacy_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    pharmacy_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    pharmacy_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

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
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'owner'

        if commit:
            user.save()

            pharmacy = Pharmacy.objects.create(
                name=self.cleaned_data['pharmacy_name'],
                email=self.cleaned_data['pharmacy_email'],
                phone=self.cleaned_data.get('pharmacy_phone'),
                address=self.cleaned_data.get('pharmacy_address'),
                owner=user
            )

            user.pharmacy = pharmacy
            user.save()

        return user


class StaffCreateForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            ('pharmacist', 'Pharmacist'),
            ('cashier', 'Cashier'),
            ('staff', 'Staff'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        self.pharmacy = kwargs.pop('pharmacy', None)
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.pharmacy = self.pharmacy

        if commit:
            user.save()

        return user


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