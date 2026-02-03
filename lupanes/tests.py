from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone

from lupanes.models import DeliveryNote, Producer, Product, ProductPrice
from lupanes.users import CUSTOMERS_GROUP

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
