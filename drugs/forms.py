from django import forms
from .models import Drug


class DrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = [
            'drug_name',
            'category',
            'batch_number',
            'quantity',
            'unit_price',
            'expiry_date',
            'manufacturer',
        ]
        widgets = {
            'drug_name': forms.TextInput(attrs={'placeholder': 'e.g. Paracetamol'}),
            'category': forms.TextInput(attrs={'placeholder': 'e.g. Tablet'}),
            'batch_number': forms.TextInput(attrs={'placeholder': 'Enter batch number'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'unit_price': forms.NumberInput(attrs={'placeholder': 'Enter unit price'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'manufacturer': forms.TextInput(attrs={'placeholder': 'Manufacturer name'}),
        }