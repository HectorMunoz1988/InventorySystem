from django import forms

from .models import StockMovement


class StockMovementForm(forms.ModelForm):

    class Meta:
        model = StockMovement
        fields = ['movement_type', 'quantity']

        widgets = {
            'movement_type': forms.Select(),
            'quantity': forms.NumberInput(
                attrs={
                    'min': 1
                }
            )
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity < 1:
            raise forms.ValidationError(
                'La cantidad debe ser mayor que 0.'
            )

        return quantity