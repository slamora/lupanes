from django import forms
from django.core.exceptions import ValidationError

from lupanes.models import Customer, DeliveryNote


class CustomerAuthForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        data = self.cleaned_data["email"]
        try:
            customer = Customer.objects.get(email=data)
        except Customer.DoesNotExist:
            raise ValidationError("No se ha encontrado ninguna nevera con el correo proporcionado.")
        else:
            self.customer_id = customer.pk
        return data


class DeliveryNoteCreateForm(forms.ModelForm):
    class Meta:
        model = DeliveryNote
        fields = ["product", "quantity"]

    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop("customer")
        return super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.customer = self.customer
        instance = super().save(commit)
        return instance
