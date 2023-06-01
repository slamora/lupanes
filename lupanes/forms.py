from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from lupanes.models import DeliveryNote, ProductPrice

User = get_user_model()


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


class NotifyMissingProductForm(forms.Form):
    product = forms.CharField(
        label="Producto",
        help_text="Trata de ser lo más descriptivo posible. Incluye el nombre del productor."
    )
    quantity = forms.DecimalField(label="Cantidad")
    unit = forms.CharField(label="Unidad")
    comment = forms.CharField(
        label="Comentario",
        widget=forms.Textarea,
        required=False,
        help_text="¿Algo más que añadir?"
    )


class ProductPriceForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.SelectDateWidget())

    class Meta:
        model = ProductPrice
        fields = ["start_date", "value"]

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product")
        return super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        if self.product.productprice_set.filter(start_date=start_date).exists():
            self.add_error("start_date", ValidationError("Ya existe precio para esa fecha", code="invalid"))

        return cleaned_data

    def save(self, commit=True):
        self.instance.product = self.product
        instance = super().save(commit)
        return instance
