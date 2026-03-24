from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from pharmacies.models import Pharmacy


# ===============================
# PHARMACY REGISTRATION (OWNER)
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

    def save(self, commit=True):
        # ✅ Save user first
        user = super().save(commit=False)

        if commit:
            user.save()

            # ✅ Create pharmacy and link owner
            pharmacy = Pharmacy.objects.create(
                name=self.cleaned_data['pharmacy_name'],
                email=self.cleaned_data['pharmacy_email'],
                phone=self.cleaned_data.get('pharmacy_phone'),
                address=self.cleaned_data.get('pharmacy_address'),
                owner=user  # 🔥 THIS IS THE FIX
            )

            # ✅ Attach user to pharmacy
            user.pharmacy = pharmacy
            user.save()

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# ===============================
# STAFF CREATION (BY OWNER)
# ===============================
class StaffCreateForm(UserCreationForm):

    # ❗ Restrict roles (no owner here)
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
        # 🔥 Get pharmacy from view
        self.pharmacy = kwargs.pop('pharmacy', None)

        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)

        # ✅ Assign pharmacy automatically
        if self.pharmacy:
            user.pharmacy = self.pharmacy

        if commit:
            user.save()

        return user


# ===============================
# LOGIN FORM
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