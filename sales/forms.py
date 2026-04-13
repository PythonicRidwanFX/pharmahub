from django import forms
from .models import Sale
from drugs.models import Drug


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['drug', 'customer_name', 'quantity', 'unit_price', 'note']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quantity'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unit price',
                'id': 'unit-price-field'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter note',
                'rows': 4
            }),
        }

    def __init__(self, *args, **kwargs):
        pharmacy = kwargs.pop('pharmacy', None)
        super().__init__(*args, **kwargs)

        if pharmacy:
            self.fields['drug'].queryset = Drug.objects.filter(
                pharmacy=pharmacy,
                quantity__gt=0
            ).order_by('drug_name')

        self.fields['drug'].widget.attrs.update({
            'class': 'form-control',
            'id': 'drug-select'
        })

        self.fields['drug'].label_from_instance = lambda obj: (
            f"{obj.drug_name} — Stock: {obj.quantity}"
            + (f" — Batch: {obj.batch_number}" if obj.batch_number else "")
        )