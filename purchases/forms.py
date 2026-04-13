from django import forms
from .models import Purchase
from drugs.models import Drug


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['drug', 'supplier', 'quantity', 'purchase_price', 'note']
        widgets = {
            'supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter supplier name'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quantity'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purchase price',
                'id': 'purchase-price-field'
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
                pharmacy=pharmacy
            ).order_by('drug_name')

        self.fields['drug'].widget.attrs.update({
            'class': 'form-control',
            'id': 'drug-select'
        })

        self.fields['drug'].label_from_instance = lambda obj: (
            f"{obj.drug_name} — Stock: {obj.quantity}"
            + (f" — Batch: {obj.batch_number}" if obj.batch_number else "")
        )