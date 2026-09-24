from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.formats import date_format

from lupanes.exceptions import PriceDoesNotExistOnDate


class DeliveryNote(models.Model):
    """Albarán"""
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                   related_name="registered_notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(default=timezone.now)
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    quantity = models.DecimalField("Cantidad", max_digits=6, decimal_places=3)
    sheet_number = models.CharField("Nº de hoja", max_length=6, blank=True, default='')

    def amount(self):
        return self.quantity * self.product.get_price_on(self.date)

    def get_amount_export_format(self):
        return '{0:.2f}'.format(self.amount())


class GroupOrder(models.Model):
    """Pedido de grupo: a time-boxed group buy coordinated by a member."""

    class Status(models.TextChoices):
        OPEN = "open", "Abierto"
        CLOSED = "closed", "Cerrado"
        ORDERED = "ordered", "Pedido al productor"
        ARRIVED = "arrived", "Recibido"

    _STATUS_RANK = {
        Status.OPEN: 0,
        Status.CLOSED: 1,
        Status.ORDERED: 2,
        Status.ARRIVED: 3,
    }

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="group_orders_created")
    title = models.CharField("Título", max_length=200)
    producer_name = models.CharField("Productor", max_length=200)
    description = models.TextField("Descripción", blank=True, default="")
    closing_date = models.DateTimeField("Fecha de cierre")
    estimated_delivery_date = models.DateField("Fecha estimada de entrega", null=True, blank=True)
    paid_in_albaranes = models.BooleanField("El pago se registra en albaranes", default=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    arrived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def is_open(self):
        """Open for submissions: status OPEN and the closing date has not passed."""
        return self.status == self.Status.OPEN and self.closing_date > timezone.now()

    def can_advance_to(self, target):
        """The lifecycle is forward-only (open → closed → ordered → arrived)."""
        if target not in self._STATUS_RANK:
            return False
        return self._STATUS_RANK[target] > self._STATUS_RANK[self.status]


class GroupOrderProduct(models.Model):
    """A freeform orderable line of a group order (no link to the catalog Product)."""
    group_order = models.ForeignKey(GroupOrder, on_delete=models.CASCADE, related_name="products")
    name = models.CharField("Producto", max_length=200)
    price = models.DecimalField("Precio", max_digits=8, decimal_places=2, null=True, blank=True)
    unit = models.CharField("Unidad", max_length=32, blank=True, default="")
    notes = models.CharField("Notas", max_length=255, blank=True, default="")

    def __str__(self) -> str:
        return self.name


class GroupOrderLineItem(models.Model):
    """A member's requested quantity for one product of a group order."""
    product = models.ForeignKey(GroupOrderProduct, on_delete=models.CASCADE, related_name="line_items")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                 related_name="group_order_line_items")
    quantity = models.DecimalField("Cantidad", max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "customer")

    def __str__(self) -> str:
        return f"{self.customer} - {self.product} ({self.quantity})"

    @property
    def group_order(self):
        return self.product.group_order


class Producer(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"


class Product(models.Model):
    class Unit(models.TextChoices):
        BOTE = "bote"
        BOTELLA = "botella"
        DOCENA = "docena"
        GARRAFA = "garrafa"
        KG = "Kg"
        PAQUETE = "paquete"
        LITRO = "litro"
        UNIDAD = "unidad"

        @classmethod
        def fractional_units(cls):
            return [cls.KG]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    producer = models.ForeignKey("Producer", on_delete=models.PROTECT)
    unit = models.CharField(max_length=16, choices=Unit.choices)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        if self.producer.name:
            return f"{self.name} ({self.producer.name})"
        return f"{self.name}"

    def unit_accept_decimals(self):
        return self.unit in Product.Unit.fractional_units()

    def get_current_price(self):
        return self.get_price_on(timezone.now())

    def get_price_on(self, date=None):
        if date is None:
            date = timezone.now()
        try:
            pprice = self.productprice_set.filter(start_date__lte=date).latest("start_date")
        except ProductPrice.DoesNotExist:
            short_date = date_format(date, settings.SHORT_DATE_FORMAT)
            raise PriceDoesNotExistOnDate(f"Price for product {self.pk} {self.name} does not exist on {short_date}")
        return pprice.value


class ProductPrice(models.Model):
    value = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["product", "start_date"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.value} ({self.start_date})"
