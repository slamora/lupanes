from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from lupanes.models import DeliveryNote, Producer, Product, ProductPrice

User = get_user_model()


class ProductSummaryTestMixin:
    """Shared setup for product summary tests."""

    @classmethod
    def setUpTestData(cls):
        cls.managers_group = Group.objects.create(name="tienda")
        cls.customers_group = Group.objects.create(name="neveras")

        cls.manager = User.objects.create_user(username="manager", password="test1234")
        cls.manager.groups.add(cls.managers_group)

        cls.customer1 = User.objects.create_user(username="ana", password="test1234")
        cls.customer1.groups.add(cls.customers_group)

        cls.customer2 = User.objects.create_user(username="pedro", password="test1234")
        cls.customer2.groups.add(cls.customers_group)

        cls.producer = Producer.objects.create(name="Frutas Garcia")

        cls.manzana = Product.objects.create(
            name="Manzana", producer=cls.producer, unit="Kg"
        )
        ProductPrice.objects.create(
            product=cls.manzana, value=Decimal("2.50"), start_date=date(2026, 1, 1)
        )

        cls.aguacate = Product.objects.create(
            name="Aguacate", producer=cls.producer, unit="Kg"
        )
        ProductPrice.objects.create(
            product=cls.aguacate, value=Decimal("5.80"), start_date=date(2026, 1, 1)
        )

        cls.pan = Product.objects.create(
            name="Pan", producer=Producer.objects.create(name="Panaderia Local"), unit="unidad"
        )
        ProductPrice.objects.create(
            product=cls.pan, value=Decimal("1.20"), start_date=date(2026, 1, 1)
        )

        # Delivery notes for March 31
        cls.note1 = DeliveryNote.objects.create(
            customer=cls.customer1, product=cls.manzana,
            quantity=Decimal("2.500"),
            date=timezone.datetime(2026, 3, 31, 10, 0, tzinfo=timezone.utc),
        )
        cls.note2 = DeliveryNote.objects.create(
            customer=cls.customer2, product=cls.manzana,
            quantity=Decimal("3.000"),
            date=timezone.datetime(2026, 3, 31, 11, 0, tzinfo=timezone.utc),
        )
        cls.note3 = DeliveryNote.objects.create(
            customer=cls.customer1, product=cls.aguacate,
            quantity=Decimal("1.000"),
            date=timezone.datetime(2026, 3, 31, 10, 0, tzinfo=timezone.utc),
        )

        # Delivery notes for April 1
        cls.note4 = DeliveryNote.objects.create(
            customer=cls.customer2, product=cls.manzana,
            quantity=Decimal("1.500"),
            date=timezone.datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc),
        )
        cls.note5 = DeliveryNote.objects.create(
            customer=cls.customer2, product=cls.aguacate,
            quantity=Decimal("0.500"),
            date=timezone.datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc),
        )

        # Delivery note for Pan (different producer)
        cls.note6 = DeliveryNote.objects.create(
            customer=cls.customer1, product=cls.pan,
            quantity=Decimal("2"),
            date=timezone.datetime(2026, 3, 31, 10, 0, tzinfo=timezone.utc),
        )

        cls.url = reverse("lupanes:product-summary")


class ProductSummaryAccessTest(ProductSummaryTestMixin, TestCase):
    def test_anonymous_user_is_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_cannot_access(self):
        self.client.login(username="ana", password="test1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_manager_can_access(self):
        self.client.login(username="manager", password="test1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ProductSummaryNoFiltersTest(ProductSummaryTestMixin, TestCase):
    def setUp(self):
        self.client.login(username="manager", password="test1234")

    def test_shows_all_products_without_filters(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        products = response.context["product_summary"]
        product_names = [p["product__name"] for p in products]
        self.assertIn("Manzana", product_names)
        self.assertIn("Aguacate", product_names)
        self.assertIn("Pan", product_names)


class ProductSummaryDateFilterTest(ProductSummaryTestMixin, TestCase):
    def setUp(self):
        self.client.login(username="manager", password="test1234")

    def test_filter_by_date_range(self):
        response = self.client.get(self.url, {
            "date_from": "2026-03-31",
            "date_to": "2026-03-31",
        })
        products = response.context["product_summary"]
        product_names = [p["product__name"] for p in products]
        # Only March 31 notes: Manzana, Aguacate, Pan
        self.assertIn("Manzana", product_names)
        self.assertIn("Aguacate", product_names)
        self.assertIn("Pan", product_names)

        # Manzana on March 31: 2.5 + 3.0 = 5.5
        manzana = next(p for p in products if p["product__name"] == "Manzana")
        self.assertEqual(manzana["total_qty"], Decimal("5.500"))

    def test_filter_excludes_notes_outside_range(self):
        response = self.client.get(self.url, {
            "date_from": "2026-04-01",
            "date_to": "2026-04-01",
        })
        products = response.context["product_summary"]
        product_names = [p["product__name"] for p in products]
        # Only April 1 notes: Manzana (1.5), Aguacate (0.5)
        self.assertIn("Manzana", product_names)
        self.assertIn("Aguacate", product_names)
        self.assertNotIn("Pan", product_names)

        manzana = next(p for p in products if p["product__name"] == "Manzana")
        self.assertEqual(manzana["total_qty"], Decimal("1.500"))


class ProductSummaryProductFilterTest(ProductSummaryTestMixin, TestCase):
    def setUp(self):
        self.client.login(username="manager", password="test1234")

    def test_filter_by_single_product(self):
        response = self.client.get(self.url, {
            "products": [self.aguacate.pk],
        })
        products = response.context["product_summary"]
        product_names = [p["product__name"] for p in products]
        self.assertEqual(product_names, ["Aguacate"])

    def test_filter_by_multiple_products(self):
        response = self.client.get(self.url, {
            "products": [self.manzana.pk, self.aguacate.pk],
        })
        products = response.context["product_summary"]
        product_names = sorted([p["product__name"] for p in products])
        self.assertEqual(product_names, ["Aguacate", "Manzana"])

    def test_combined_product_and_date_filter(self):
        response = self.client.get(self.url, {
            "products": [self.manzana.pk],
            "date_from": "2026-03-31",
            "date_to": "2026-03-31",
        })
        products = response.context["product_summary"]
        self.assertEqual(len(products), 1)

        manzana = products[0]
        self.assertEqual(manzana["product__name"], "Manzana")
        self.assertEqual(manzana["total_qty"], Decimal("5.500"))


class ProductSummaryAggregationTest(ProductSummaryTestMixin, TestCase):
    def setUp(self):
        self.client.login(username="manager", password="test1234")

    def test_aggregates_quantity_per_product(self):
        response = self.client.get(self.url, {
            "date_from": "2026-03-31",
            "date_to": "2026-04-01",
        })
        products = response.context["product_summary"]
        manzana = next(p for p in products if p["product__name"] == "Manzana")
        # 2.5 + 3.0 + 1.5 = 7.0
        self.assertEqual(manzana["total_qty"], Decimal("7.000"))

    def test_aggregates_amount_per_product(self):
        response = self.client.get(self.url, {
            "date_from": "2026-03-31",
            "date_to": "2026-04-01",
        })
        products = response.context["product_summary"]
        manzana = next(p for p in products if p["product__name"] == "Manzana")
        # 7.0 kg * 2.50 = 17.50
        # Note: amount is calculated per-note (qty * price_on_date), so this tests
        # that the view aggregates note amounts, not just qty * current_price
        self.assertEqual(manzana["total_amount"], Decimal("17.50"))

    def test_shows_totals_in_context(self):
        response = self.client.get(self.url, {
            "date_from": "2026-03-31",
            "date_to": "2026-04-01",
        })
        totals = response.context["totals"]
        # Total amount: Manzana 17.50 + Aguacate 8.70 + Pan 2.40 = 28.60
        self.assertEqual(totals["total_amount"], Decimal("28.60"))

    def test_empty_result_for_no_matching_notes(self):
        response = self.client.get(self.url, {
            "date_from": "2025-01-01",
            "date_to": "2025-01-31",
        })
        products = response.context["product_summary"]
        self.assertEqual(len(products), 0)
