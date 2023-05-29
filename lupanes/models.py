from django.conf import settings
from django.db import models
from django.utils import timezone


class DeliveryNote(models.Model):
    """Albarán"""
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    quantity = models.DecimalField("Cantidad", max_digits=6, decimal_places=3)

    def amount(self):
        return self.quantity * self.product.get_price_on(self.date)


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
        pprice = self.productprice_set.filter(start_date__lte=date).latest("start_date")
        return pprice.value


class ProductPrice(models.Model):
    value = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["product", "start_date"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.value} ({self.start_date})"
