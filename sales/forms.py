from django import forms
from .models import Sale
from drugs.models import Drug


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['drug', 'customer_name', 'quantity', 'unit_price', 'note']

    def __init__(self, *args, **kwargs):
        pharmacy = kwargs.pop('pharmacy', None)
        super().__init__(*args, **kwargs)

        if pharmacy:
            self.fields['drug'].queryset = Drug.objects.filter(
                pharmacy=pharmacy,
                quantity__gt=0
            )