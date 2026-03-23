from django import forms
from .models import Purchase
from drugs.models import Drug


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['drug', 'supplier', 'quantity', 'purchase_price', 'note']

    def __init__(self, *args, **kwargs):
        pharmacy = kwargs.pop('pharmacy', None)
        super().__init__(*args, **kwargs)

        if pharmacy:
            self.fields['drug'].queryset = Drug.objects.filter(pharmacy=pharmacy)