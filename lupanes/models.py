from django.db import models


class Customer(models.Model):
    """Nevera"""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)


class DeliveryNote(models.Model):
    """Albarán"""
    customer = models.ForeignKey("Customer", on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    quantity = models.DecimalField("Cantidad", max_digits=6, decimal_places=3)


class Producer(models.Model):
    name = models.CharField(max_length=255)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    producer = models.ForeignKey("Producer", on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)


class ProductPrice(models.Model):
    value = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
