from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from lupanes.models import DeliveryNote, Producer, Product, ProductPrice
from django.db.models.functions import Lower

User = get_user_model()


class DeliveryNoteCreateForm(forms.ModelForm):
    """Form to register day shop by neveras"""
    product = forms.ModelChoiceField(
        label="Producto",
        queryset=Product.objects.filter(is_active=True).order_by(Lower('name'))
    )

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


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class DateTimeLocalField(forms.DateTimeField):
    # Set DATETIME_INPUT_FORMATS here because, if USE_L10N
    # is True, the locale-dictated format will be applied
    # instead of settings.DATETIME_INPUT_FORMATS.
    # See also:
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Date_and_time_formats

    input_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M"
    ]
    widget = DateTimeLocalInput(format="%Y-%m-%dT%H:%M")


class DeliveryNoteForm(forms.ModelForm):
    """Form to digitalize albaranes by tienda group"""
    customer = forms.ModelChoiceField(
        label="Nevera",
        queryset=User.objects.get_active_customers(),
    )
    # allow to select all products (even inactive)
    product = forms.ModelChoiceField(
        label="Producto",
        queryset=Product.objects.all().order_by(Lower('name'))
    )
    date = DateTimeLocalField()

    class Meta:
        model = DeliveryNote
        fields = ["sheet_number", "customer", "product", "quantity", "date"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        return super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.created_by = self.user
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


class ProductForm(forms.ModelForm):
    producer = forms.ModelChoiceField(
        queryset=Producer.objects.all().order_by(Lower('name'))
    )
    is_active = forms.BooleanField(
        label="¿Activo?", help_text="En lugar de eliminar un producto, márcalo como inactivo.", required=False)

    class Meta:
        model = Product
        fields = ["name", "unit", "producer", "is_active"]


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
