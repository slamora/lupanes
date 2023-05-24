from django import forms
from django.core.exceptions import ValidationError

from lupanes.models import Customer, DeliveryNote, ProductPrice


class CustomerAuthForm(forms.Form):
    name = forms.CharField()

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        try:
            customer = Customer.objects.get(name__iexact=name)
        except Customer.DoesNotExist:
            raise ValidationError("No se ha encontrado ninguna nevera con el nombre proporcionado.")
        else:
            self.customer_id = customer.pk
        return customer.name


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


class ProductPriceForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.SelectDateWidget())

    class Meta:
        model = ProductPrice
        fields = ["start_date", "value"]

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product")
        return super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.product = self.product
        instance = super().save(commit)
        return instance
