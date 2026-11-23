"""Unit tests for group-order model logic (is_open, forward-only lifecycle)."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from lupanes.models import GroupOrder

User = get_user_model()


class GroupOrderModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create_user(username="gloria", password="x")

    def _make(self, status=GroupOrder.Status.OPEN, closing_in_days=3):
        return GroupOrder.objects.create(
            created_by=self.creator,
            title="Pan",
            producer_name="Aineto",
            closing_date=timezone.now() + timedelta(days=closing_in_days),
            status=status,
        )

    def test_is_open_when_open_and_closing_date_in_future(self):
        self.assertTrue(self._make().is_open())

    def test_not_open_when_status_is_closed(self):
        self.assertFalse(self._make(status=GroupOrder.Status.CLOSED).is_open())

    def test_not_open_when_closing_date_has_passed(self):
        order = self._make(closing_in_days=-1)
        self.assertFalse(order.is_open())

    def test_can_advance_forward(self):
        order = self._make(status=GroupOrder.Status.OPEN)
        self.assertTrue(order.can_advance_to(GroupOrder.Status.CLOSED))
        self.assertTrue(order.can_advance_to(GroupOrder.Status.ARRIVED))

    def test_cannot_advance_backwards_or_sideways(self):
        order = self._make(status=GroupOrder.Status.ORDERED)
        self.assertFalse(order.can_advance_to(GroupOrder.Status.OPEN))
        self.assertFalse(order.can_advance_to(GroupOrder.Status.ORDERED))

    def test_cannot_advance_to_unknown_status(self):
        order = self._make()
        self.assertFalse(order.can_advance_to("bogus"))
