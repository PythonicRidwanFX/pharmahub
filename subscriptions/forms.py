from django import forms
from .models import Plan


class PlanSelectForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.filter(is_active=True),
        empty_label="Select a plan"
    )