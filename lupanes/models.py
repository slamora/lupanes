from difflib import SequenceMatcher

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.formats import date_format

from lupanes.exceptions import PriceDoesNotExistOnDate


class DeliveryNote(models.Model):
    """Albarán"""

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="registered_notes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date = models.DateTimeField(default=timezone.now)
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    quantity = models.DecimalField("Cantidad", max_digits=6, decimal_places=3)
    sheet_number = models.CharField("Nº de hoja", max_length=6, blank=True, default="")

    def amount(self):
        return self.quantity * self.product.get_price_on(self.date)

    def get_amount_export_format(self):
        return "{0:.2f}".format(self.amount())


class Producer(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"


class ProductManager(models.Manager):
    @staticmethod
    def _normalize_name(name: str) -> str:
        """Strip extra spaces and normalize casing for comparison."""
        return " ".join(name.strip().lower().split())

    def find_similar(
        self,
        name: str,
        threshold: float = 0.8,
        exclude_id: int | None = None,
        only_active: bool = True,
    ) -> list[tuple["Product", float]]:
        """
        Check if a given name is similar to any existing product.

        :param name: Candidate name string.
        :param threshold: Similarity score between 0.0 and 1.0 (default 0.8 / 80%).
        :param exclude_id: Optional PK to exclude (useful when editing an existing product).
        :param only_active: When True, checks only active products.
        :return: List of tuples (product_instance, similarity_score) sorted by highest similarity.
        """
        target_name = self._normalize_name(name)
        if not target_name:
            return []

        qs = self.get_queryset()
        if only_active:
            qs = qs.filter(is_active=True)
        if exclude_id is not None:
            qs = qs.exclude(pk=exclude_id)

        # Optimize DB query: fetch only pk and name into memory
        products = list(qs.only("id", "name"))

        results = []
        for product in products:
            existing_name = self._normalize_name(product.name)

            # Quick exact match shortcut
            if target_name == existing_name:
                results.append((product, 1.0))
                continue

            score = SequenceMatcher(None, target_name, existing_name).ratio()
            if score >= threshold:
                results.append((product, round(score, 3)))

        # Sort descending by match score
        results.sort(key=lambda item: item[1], reverse=True)
        return results

    def detect_existing_duplicates(
        self,
        threshold: float = 0.85,
        only_active: bool = True,
    ) -> list[dict]:
        """
        Scan all stored products to find pairs or clusters of potential duplicates.

        :param threshold: Minimum similarity ratio to flag as duplicate.
        :param only_active: When True, checks only active products.
        :return: List of dicts: [{'product_a': p1, 'product_b': p2, 'similarity': score}, ...]
        """
        qs = self.get_queryset()
        if only_active:
            qs = qs.filter(is_active=True)

        products = list(qs.only("id", "name"))
        normalized = [self._normalize_name(p.name) for p in products]

        duplicates = []
        total = len(products)

        # Compare combinations (i < j) to avoid reverse duplicate pairs
        for i in range(total):
            for j in range(i + 1, total):
                score = SequenceMatcher(None, normalized[i], normalized[j]).ratio()
                if score >= threshold:
                    duplicates.append(
                        {
                            "product_a": products[i],
                            "product_b": products[j],
                            "similarity": round(score, 3),
                        }
                    )

        duplicates.sort(key=lambda item: item["similarity"], reverse=True)
        return duplicates


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

    objects = ProductManager()

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
            pprice = self.productprice_set.filter(start_date__lte=date).latest(
                "start_date"
            )
        except ProductPrice.DoesNotExist:
            short_date = date_format(date, settings.SHORT_DATE_FORMAT)
            raise PriceDoesNotExistOnDate(
                f"Price for product {self.pk} {self.name} does not exist on {short_date}"
            )
        return pprice.value


class ProductPrice(models.Model):
    value = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["product", "start_date"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.value} ({self.start_date})"
