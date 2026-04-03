from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import requests.exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from gspread.exceptions import APIError

import lupanes.utils
from lupanes.exceptions import RetryExhausted
from lupanes.models import DeliveryNote, Producer, Product, ProductPrice
from lupanes.users import CUSTOMERS_GROUP
from lupanes.utils import _get_nevera_cache_key, search_nevera_balance

User = get_user_model()


class UserMonthlyConsumptionTestCase(TestCase):
    """Tests para current_month_consumption y projected_balance"""

    def setUp(self):
        """Configuración común para todos los tests"""
        # Crear grupo de neveras
        self.customers_group = Group.objects.create(name=CUSTOMERS_GROUP)

        # Crear usuario nevera
        self.customer = User.objects.create_user(
            username="test_nevera",
            email="test@example.com",
            password="testpass123"
        )
        self.customer.groups.add(self.customers_group)

        # Crear usuario no-nevera
        self.non_customer = User.objects.create_user(
            username="non_customer",
            email="non@example.com",
            password="testpass123"
        )

        # Crear productor y producto
        self.producer = Producer.objects.create(name="Test Producer")
        self.product = Product.objects.create(
            name="Test Product",
            producer=self.producer,
            unit=Product.Unit.KG,
            is_active=True
        )

        # Crear precio para el producto
        self.price = ProductPrice.objects.create(
            product=self.product,
            value=Decimal("10.00"),
            start_date=timezone.now().date() - timezone.timedelta(days=30)
        )

    def test_current_month_consumption_no_notes(self):
        """Test: consumo del mes sin albaranes debe ser 0"""
        consumption = self.customer.current_month_consumption()
        self.assertEqual(consumption, Decimal("0"))

    def test_current_month_consumption_with_notes_current_month(self):
        """Test: consumo del mes con albaranes del mes actual"""
        now = timezone.now()

        # Crear 3 albaranes en el mes actual
        DeliveryNote.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=Decimal("2.5"),  # 2.5 * 10 = 25
            date=now
        )
        DeliveryNote.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=Decimal("1.0"),  # 1.0 * 10 = 10
            date=now
        )
        DeliveryNote.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=Decimal("0.5"),  # 0.5 * 10 = 5
            date=now
        )

        consumption = self.customer.current_month_consumption()
        # Total: 25 + 10 + 5 = 40
        self.assertEqual(consumption, Decimal("40.00"))

    def test_current_month_consumption_ignores_previous_months(self):
        """Test: consumo del mes NO incluye albaranes de meses anteriores"""
        now = timezone.now()
        last_month = now - timezone.timedelta(days=35)

        # Albarán del mes pasado (no debe contarse)
        DeliveryNote.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=Decimal("5.0"),
            date=last_month
        )

        # Albarán del mes actual (sí debe contarse)
        DeliveryNote.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=Decimal("2.0"),  # 2.0 * 10 = 20
            date=now
        )

        consumption = self.customer.current_month_consumption()
        # Solo debe contar el del mes actual
        self.assertEqual(consumption, Decimal("20.00"))

    def test_current_month_consumption_non_customer_returns_zero(self):
        """Test: usuario no-nevera debe retornar 0"""
        consumption = self.non_customer.current_month_consumption()
        self.assertEqual(consumption, Decimal("0"))

    def test_current_month_consumption_handles_price_errors(self):
        """Test: maneja errores al calcular precios (producto sin precio)"""
        now = timezone.now()

        # Crear producto sin precio
        product_no_price = Product.objects.create(
            name="Product Without Price",
            producer=self.producer,
            unit=Product.Unit.KG,
            is_active=True
        )

        # Albarán con producto sin precio (debe ignorarse)
        DeliveryNote.objects.create(
            customer=self.customer,
            product=product_no_price,
            quantity=Decimal("1.0"),
            date=now
        )

        # Albarán con producto con precio (debe contarse)
        DeliveryNote.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=Decimal("3.0"),  # 3.0 * 10 = 30
            date=now
        )

        consumption = self.customer.current_month_consumption()
        # Solo debe contar el que tiene precio
        self.assertEqual(consumption, Decimal("30.00"))

    @patch('lupanes.users.models.User.current_balance', new_callable=lambda: property(lambda self: Decimal("100.00")))
    def test_projected_balance_positive(self, mock_balance):
        """Test: previsión de saldo positiva"""
        now = timezone.now()

        # Crear albarán con consumo de 30€
        DeliveryNote.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=Decimal("3.0"),  # 3.0 * 10 = 30
            date=now
        )

        projected = self.customer.projected_balance()
        # 100 - 30 = 70
        self.assertEqual(projected, Decimal("70.00"))

    @patch('lupanes.users.models.User.current_balance', new_callable=lambda: property(lambda self: Decimal("50.00")))
    def test_projected_balance_negative(self, mock_balance):
        """Test: previsión de saldo negativa"""
        now = timezone.now()

        # Crear albarán con consumo de 80€
        DeliveryNote.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=Decimal("8.0"),  # 8.0 * 10 = 80
            date=now
        )

        projected = self.customer.projected_balance()
        # 50 - 80 = -30
        self.assertEqual(projected, Decimal("-30.00"))

    @patch('lupanes.users.models.User.current_balance', new_callable=lambda: property(lambda self: Decimal("100.00")))
    def test_projected_balance_no_consumption(self, mock_balance):
        """Test: previsión de saldo sin consumo (igual al saldo actual)"""
        projected = self.customer.projected_balance()
        # 100 - 0 = 100
        self.assertEqual(projected, Decimal("100.00"))

    @patch('lupanes.users.models.User.current_balance', new_callable=lambda: property(lambda self: None))
    def test_projected_balance_no_balance_returns_none(self, mock_balance):
        """Test: previsión de saldo cuando no hay saldo disponible"""
        projected = self.customer.projected_balance()
        self.assertIsNone(projected)

    @patch('lupanes.users.models.User.current_balance', new_callable=lambda: property(lambda self: "N/A"))
    def test_projected_balance_na_balance_returns_none(self, mock_balance):
        """Test: previsión de saldo cuando el saldo es N/A"""
        projected = self.customer.projected_balance()
        self.assertIsNone(projected)

    def test_projected_balance_non_customer_returns_none(self):
        """Test: usuario no-nevera debe retornar None"""
        projected = self.non_customer.projected_balance()
        self.assertIsNone(projected)


class RetryLogicTestCase(TestCase):
    """Tests for retry logic with exponential backoff"""

    def _create_503_response(self):
        """Helper to create a mock 503 response for APIError"""
        mock_response = MagicMock()
        mock_response.text = "Service Unavailable"
        mock_response.status_code = 503
        mock_response.json.return_value = {"error": {"code": 503, "message": "Service Unavailable"}}
        return mock_response

    @patch('lupanes.utils.gspread.service_account')
    @patch('lupanes.utils.time.sleep')  # Mock sleep to speed up tests
    def test_load_spreadsheet_retries_on_503(self, mock_sleep, mock_service_account):
        """Verify retry happens on 503 error and succeeds on second attempt"""
        mock_gc = MagicMock()
        mock_worksheet = MagicMock()

        # First call raises 503, second call succeeds
        mock_gc.open_by_url.side_effect = [
            APIError(self._create_503_response()),
            MagicMock(get_worksheet=lambda x: mock_worksheet)
        ]
        mock_service_account.return_value = mock_gc

        result = lupanes.utils.load_spreadsheet()

        # Verify it was called twice (initial + 1 retry)
        self.assertEqual(mock_gc.open_by_url.call_count, 2)
        # Verify sleep was called once between retries
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(result, mock_worksheet)

    @patch('lupanes.utils.gspread.service_account')
    @patch('lupanes.utils.time.sleep')
    def test_load_spreadsheet_retries_on_request_exception(self, mock_sleep, mock_service_account):
        """Verify retry happens on RequestException"""
        mock_gc = MagicMock()
        mock_worksheet = MagicMock()

        # First call raises RequestException, second call succeeds
        mock_gc.open_by_url.side_effect = [
            requests.exceptions.RequestException("Network error"),
            MagicMock(get_worksheet=lambda x: mock_worksheet)
        ]
        mock_service_account.return_value = mock_gc

        lupanes.utils.load_spreadsheet()

        self.assertEqual(mock_gc.open_by_url.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)

    @patch('lupanes.utils.gspread.service_account')
    @patch('lupanes.utils.time.sleep')
    def test_load_spreadsheet_raises_retry_exhausted(self, mock_sleep, mock_service_account):
        """Verify RetryExhausted raised after max retries"""
        mock_gc = MagicMock()
        # Always fail with 503
        mock_gc.open_by_url.side_effect = APIError(self._create_503_response())
        mock_service_account.return_value = mock_gc

        with self.assertRaises(RetryExhausted) as context:
            lupanes.utils.load_spreadsheet()

        # Verify it tried 4 times (max_retries=4)
        self.assertEqual(mock_gc.open_by_url.call_count, 4)
        self.assertIn("Failed after", str(context.exception))

    @patch('lupanes.utils.gspread.service_account')
    @patch('lupanes.utils.time.sleep')
    def test_load_spreadsheet_exponential_backoff(self, mock_sleep, mock_service_account):
        """Verify exponential backoff delays increase properly"""
        mock_gc = MagicMock()
        mock_gc.open_by_url.side_effect = APIError(self._create_503_response())
        mock_service_account.return_value = mock_gc

        try:
            lupanes.utils.load_spreadsheet()
        except RetryExhausted:
            pass

        # Verify sleep was called with increasing delays (base_delay * 2^attempt + jitter)
        # With base_delay=1.0 and max_retries=4: ~1s, ~2s, ~4s (3 sleeps before final failure)
        self.assertEqual(mock_sleep.call_count, 3)
        delays = [call[0][0] for call in mock_sleep.call_args_list]

        # First delay should be around 1 second (with jitter 1.0-1.1)
        self.assertGreaterEqual(delays[0], 1.0)
        self.assertLess(delays[0], 1.2)

        # Second delay should be around 2 seconds (with jitter 2.0-2.2)
        self.assertGreaterEqual(delays[1], 2.0)
        self.assertLess(delays[1], 2.3)

        # Delays should increase
        self.assertGreater(delays[1], delays[0])
        self.assertGreater(delays[2], delays[1])


class CachingTestCase(TestCase):
    """Tests for caching logic in search_nevera_balance"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch('lupanes.utils.load_spreadsheet')
    def test_search_nevera_balance_caches_result(self, mock_load):
        """Verify balance is cached after first fetch"""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [
            ['nevera1', '100.50'],
        ]
        mock_load.return_value = mock_worksheet

        # First call - cache miss
        result1 = search_nevera_balance('nevera1')
        self.assertEqual(result1, '100.50')

        # Second call - cache hit (no API call)
        result2 = search_nevera_balance('nevera1')
        self.assertEqual(result2, '100.50')

        # Verify API called only once
        mock_load.assert_called_once()

    @patch('lupanes.utils.load_spreadsheet')
    def test_search_nevera_balance_caches_not_found(self, mock_load):
        """Verify 'N/A' is cached to avoid repeated lookups"""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [
            ['nevera1', '100.50'],
        ]
        mock_load.return_value = mock_worksheet

        # First call - cache miss, returns N/A
        result1 = search_nevera_balance('nonexistent')
        self.assertEqual(result1, 'N/A')

        # Second call - cache hit (no API call)
        result2 = search_nevera_balance('nonexistent')
        self.assertEqual(result2, 'N/A')

        # Verify API called only once
        mock_load.assert_called_once()

    @patch('lupanes.utils.load_spreadsheet')
    def test_search_nevera_balance_case_insensitive_cache(self, mock_load):
        """Verify cache keys are case-insensitive"""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [
            ['nevera1', '100.50'],
        ]
        mock_load.return_value = mock_worksheet

        # First call with lowercase
        result1 = search_nevera_balance('nevera1')
        self.assertEqual(result1, '100.50')

        # Second call with uppercase - should hit cache
        result2 = search_nevera_balance('NEVERA1')
        self.assertEqual(result2, '100.50')

        # Verify API called only once
        mock_load.assert_called_once()

    @patch('lupanes.utils.load_spreadsheet')
    def test_search_nevera_balance_respects_cache_ttl(self, mock_load):
        """Verify cache respects TTL setting"""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [
            ['nevera1', '100.50'],
        ]
        mock_load.return_value = mock_worksheet

        # First call
        result1 = search_nevera_balance('nevera1')
        self.assertEqual(result1, '100.50')

        # Verify cache key exists
        cache_key = _get_nevera_cache_key('nevera1')
        self.assertEqual(cache.get(cache_key), '100.50')

        # Manually delete cache to simulate expiry
        cache.delete(cache_key)

        # Next call should hit API again
        result2 = search_nevera_balance('nevera1')
        self.assertEqual(result2, '100.50')

        # Verify API called twice
        self.assertEqual(mock_load.call_count, 2)

    @patch('lupanes.utils.load_spreadsheet')
    def test_search_nevera_balance_caches_all_customers(self, mock_load):
        """Verify that one API call caches ALL customers from spreadsheet"""
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_values.return_value = [
            ['nevera1', '100.50'],
            ['nevera2', '200.75'],
            ['nevera3', '50.00'],
        ]
        mock_load.return_value = mock_worksheet

        # First call for nevera1 - cache miss, loads spreadsheet
        result1 = search_nevera_balance('nevera1')
        self.assertEqual(result1, '100.50')
        self.assertEqual(mock_load.call_count, 1)

        # Second call for nevera2 - cache hit (already cached from first call)
        result2 = search_nevera_balance('nevera2')
        self.assertEqual(result2, '200.75')
        self.assertEqual(mock_load.call_count, 1)  # Still only 1 API call

        # Third call for nevera3 - cache hit
        result3 = search_nevera_balance('nevera3')
        self.assertEqual(result3, '50.00')
        self.assertEqual(mock_load.call_count, 1)  # Still only 1 API call

        # Verify all three are in cache
        self.assertEqual(cache.get(_get_nevera_cache_key('nevera1')), '100.50')
        self.assertEqual(cache.get(_get_nevera_cache_key('nevera2')), '200.75')
        self.assertEqual(cache.get(_get_nevera_cache_key('nevera3')), '50.00')


# --- Product Summary View Tests ---


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
