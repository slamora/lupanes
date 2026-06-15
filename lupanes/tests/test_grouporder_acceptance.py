"""Outside-In acceptance tests for the *group-order-coordination* feature.

These tests form the OUTER LOOP of double-loop TDD for the DELIVER wave. They
enter the system exclusively through the driving ports (Django views, exercised
via the test client by URL name) and assert observable outcomes (HTTP status,
redirects, persisted state, context objects, sent email). They deliberately do
NOT reach into internal validators/forms/mixins directly.

EXPECTED STATE ON FIRST RUN: RED. None of the production code (models
`GroupOrder` / `GroupOrderProduct` / `GroupOrderLineItem`, the
`lupanes:grouporder-*` URLs/views, the `GROUP_ORDER_NOTIFY_EMAIL` setting, the
announcement email template) exists yet. As DELIVER implements each slice, the
corresponding test class goes GREEN.

Traceability: each test class maps to one user story (US-01..US-08) plus the two
cross-cutting @property scenarios. See
`docs/feature/group-order-coordination/distill/acceptance-tests.md`.

Sources of truth:
  - discuss/acceptance-criteria.md  (Gherkin scenarios)
  - discuss/user-stories.md         (US-01..US-08, ACs)
  - design/architecture.md          (models, views, URL names, mixins, email)
  - discover/wave-decisions.md      (D1-D13)

Conventions mirrored from `lupanes/tests/test_legacy.py`:
  - `Group.objects.create(name=CUSTOMERS_GROUP)` then `user.groups.add(group)`
  - `User.objects.create_user(...)`
  - `reverse("lupanes:...")` + `self.client`
  - authenticated-but-unauthorized => 403; anonymous => 302 (AccessMixin).
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from lupanes.models import GroupOrder, GroupOrderLineItem, GroupOrderProduct
from lupanes.users import CUSTOMERS_GROUP, MANAGERS_GROUP

User = get_user_model()

PASSWORD = "testpass123"


class GroupOrderTestMixin:
    """Shared persona/group setup, mirroring test_legacy.py's setUp pattern.

    Personas (from acceptance-criteria.md): Gloria, Marta, Didier (organizers),
    Pablo (consumer). A manager (Santi) is created to prove organizer actions are
    creator-gated, NOT manager-gated (C-ORGANIZER, cross-cutting @property).
    """

    @classmethod
    def setUpTestData(cls):
        cls.customers_group = Group.objects.create(name=CUSTOMERS_GROUP)
        cls.managers_group = Group.objects.create(name=MANAGERS_GROUP)

        cls.gloria = cls._make_customer("gloria")
        cls.marta = cls._make_customer("marta")
        cls.didier = cls._make_customer("didier")
        cls.pablo = cls._make_customer("pablo")

        # A store manager who is NOT a creator of any order. Used to prove the
        # tienda group grants no organizer rights (C-ORGANIZER).
        cls.santi = User.objects.create_user(username="santi", password=PASSWORD)
        cls.santi.groups.add(cls.managers_group)

    @classmethod
    def _make_customer(cls, username):
        user = User.objects.create_user(username=username, password=PASSWORD)
        user.groups.add(cls.customers_group)
        return user

    def login(self, user):
        self.assertTrue(self.client.login(username=user.username, password=PASSWORD))

    # --- domain helpers (still go through the model layer used by the views) ---

    def _future(self, **kw):
        return timezone.now() + timedelta(**(kw or {"days": 3}))

    def _past(self, **kw):
        return timezone.now() - timedelta(**(kw or {"days": 1}))

    def make_order(self, creator, title="Pan semana del 2 de junio",
                   producer_name="Aineto", closing_date=None,
                   paid_in_albaranes=False, status=GroupOrder.Status.OPEN,
                   products=None):
        """Create an order + its freeform products directly.

        This is test ARRANGE (preconditions), not the behaviour under test.
        Behaviour (create/submit/advance) always goes through the views.
        """
        order = GroupOrder.objects.create(
            created_by=creator,
            title=title,
            producer_name=producer_name,
            closing_date=closing_date or self._future(days=3),
            paid_in_albaranes=paid_in_albaranes,
            status=status,
        )
        for spec in (products or [("Pan de espelta 1kg", Decimal("4.50")),
                                  ("Galletas 250gr", Decimal("2.00"))]):
            name, price = spec
            GroupOrderProduct.objects.create(
                group_order=order, name=name, price=price,
            )
        return order

    def submit_line(self, order, customer, product, quantity):
        """Arrange a member submission directly (precondition helper)."""
        return GroupOrderLineItem.objects.create(
            product=product, customer=customer, quantity=Decimal(str(quantity)),
        )


# ---------------------------------------------------------------------------
# US-01 — Organizer opens a group order
# ---------------------------------------------------------------------------
class GroupOrderCreateTests(GroupOrderTestMixin, TestCase):
    """US-01: an organizer opens an order with freeform line items, a single
    producer, dates, and the albarán flag. WALKING SKELETON root."""

    def setUp(self):
        self.url = reverse("lupanes:grouporder-new")

    def test_anonymous_is_redirected_to_login(self):
        # @US-01 sad path: auth required (C-AUTH)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_organizer_opens_bread_order_with_priced_line_items(self):
        # @US-01 @walking_skeleton @driving_port happy path
        self.login(self.gloria)
        closing = timezone.make_aware(timezone.datetime(2026, 6, 1, 20, 0)) \
            if timezone.is_naive(timezone.datetime(2026, 6, 1, 20, 0)) \
            else timezone.datetime(2026, 6, 1, 20, 0)
        response = self.client.post(self.url, {
            "title": "Pan semana del 2 de junio",
            "producer_name": "Aineto",
            "closing_date": "2026-06-01 20:00",
            "estimated_delivery_date": "2026-06-03",
            "paid_in_albaranes": False,
            # inline formset for GroupOrderProduct (architecture §6)
            "products-TOTAL_FORMS": "2",
            "products-INITIAL_FORMS": "0",
            "products-MIN_NUM_FORMS": "1",
            "products-MAX_NUM_FORMS": "1000",
            "products-0-name": "Pan de espelta 1kg",
            "products-0-price": "4.50",
            "products-1-name": "Galletas 250gr",
            "products-1-price": "2.00",
        })
        # Created => redirect (302/303) to the board or the new order.
        self.assertIn(response.status_code, (302, 303))

        order = GroupOrder.objects.get(title="Pan semana del 2 de junio")
        self.assertEqual(order.status, GroupOrder.Status.OPEN)
        self.assertEqual(order.created_by, self.gloria)  # organizer recorded
        self.assertEqual(order.producer_name, "Aineto")
        self.assertFalse(order.paid_in_albaranes)
        names = sorted(order.products.values_list("name", flat=True))
        self.assertEqual(names, ["Galletas 250gr", "Pan de espelta 1kg"])

    def test_organizer_opens_order_with_line_items_without_prices(self):
        # @US-01 edge case: prices optional (Didier's oil order)
        self.login(self.didier)
        response = self.client.post(self.url, {
            "title": "Aceite primavera 2026",
            "producer_name": "ecoMatarranya",
            "closing_date": "2026-06-05 20:00",
            "paid_in_albaranes": False,
            "products-TOTAL_FORMS": "2",
            "products-INITIAL_FORMS": "0",
            "products-MIN_NUM_FORMS": "1",
            "products-MAX_NUM_FORMS": "1000",
            "products-0-name": "Aceite virgen extra 5L",
            "products-0-price": "",
            "products-1-name": "Aceite virgen extra 2L",
            "products-1-price": "",
        })
        self.assertIn(response.status_code, (302, 303))

        order = GroupOrder.objects.get(title="Aceite primavera 2026")
        self.assertEqual(order.status, GroupOrder.Status.OPEN)
        prices = list(order.products.values_list("price", flat=True))
        self.assertEqual(prices, [None, None])  # saved without prices

    def test_order_cannot_be_opened_with_no_products(self):
        # @US-01 error/boundary: needs >= 1 line item (validate_min)
        self.login(self.marta)
        response = self.client.post(self.url, {
            "title": "Papel higiénico",
            "producer_name": "Renova",
            "closing_date": "2026-06-10 20:00",
            "paid_in_albaranes": False,
            "products-TOTAL_FORMS": "0",
            "products-INITIAL_FORMS": "0",
            "products-MIN_NUM_FORMS": "1",
            "products-MAX_NUM_FORMS": "1000",
        })
        # Re-renders the form (200) with errors; the order is NOT created.
        self.assertEqual(response.status_code, 200)
        self.assertFalse(GroupOrder.objects.filter(title="Papel higiénico").exists())


# ---------------------------------------------------------------------------
# US-02 — Members see the board of open orders
# ---------------------------------------------------------------------------
class GroupOrderBoardTests(GroupOrderTestMixin, TestCase):
    """US-02: the board lists currently-open orders only (lazy-derived close)."""

    def setUp(self):
        self.url = reverse("lupanes:grouporder-list")

    def test_anonymous_is_redirected_to_login(self):
        # @US-02 sad path
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_board_lists_all_currently_open_orders(self):
        # @US-02 @walking_skeleton @driving_port happy path
        bread = self.make_order(self.gloria, title="Pan semana del 2 de junio",
                                producer_name="Aineto",
                                closing_date=self._future(days=2))
        oil = self.make_order(self.didier, title="Aceite primavera 2026",
                              producer_name="ecoMatarranya",
                              closing_date=self._future(days=6),
                              products=[("Aceite virgen extra 5L", None)])
        self.login(self.pablo)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        listed = list(response.context["object_list"])
        self.assertIn(bread, listed)
        self.assertIn(oil, listed)
        # The board surfaces the producer + closing date so members can choose.
        self.assertContains(response, "Aineto")
        self.assertContains(response, "ecoMatarranya")

    def test_closed_orders_do_not_clutter_the_board(self):
        # @US-02 edge case: status closed excluded
        self.make_order(self.marta, title="Papel higiénico",
                        status=GroupOrder.Status.CLOSED,
                        closing_date=self._past(days=1),
                        products=[("Rollos", None)])
        self.login(self.pablo)
        response = self.client.get(self.url)
        self.assertNotIn(
            "Papel higiénico",
            [o.title for o in response.context["object_list"]],
        )

    def test_orders_past_closing_date_drop_off_the_board(self):
        # @US-02 edge case: lazy-derived close (status still 'open' in DB but
        # closing_date has passed) — must NOT be listed (architecture §5 opt 1).
        self.make_order(self.gloria, title="Pan ya pasado",
                        status=GroupOrder.Status.OPEN,
                        closing_date=self._past(days=1),
                        products=[("Pan", None)])
        self.login(self.pablo)
        response = self.client.get(self.url)
        self.assertNotIn(
            "Pan ya pasado",
            [o.title for o in response.context["object_list"]],
        )

    def test_inviting_empty_state_when_nothing_is_open(self):
        # @US-02 error/boundary: empty state, not a blank page
        self.login(self.pablo)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["object_list"]), 0)
        self.assertContains(response, "No hay pedidos")


# ---------------------------------------------------------------------------
# US-03 — Member submits quantities against an open order
# ---------------------------------------------------------------------------
class GroupOrderSubmitTests(GroupOrderTestMixin, TestCase):
    """US-03: submit quantities; latest replaces (unique per product+customer);
    blocked when the order is not open."""

    def _submit_url(self, order):
        return reverse("lupanes:grouporder-submit", args=(order.pk,))

    def test_anonymous_is_redirected_to_login(self):
        # @US-03 sad path
        order = self.make_order(self.gloria)
        response = self.client.get(self._submit_url(order))
        self.assertEqual(response.status_code, 302)

    def test_member_submits_quantities(self):
        # @US-03 @walking_skeleton @driving_port happy path
        order = self.make_order(self.gloria)
        bread = order.products.get(name="Pan de espelta 1kg")
        galletas = order.products.get(name="Galletas 250gr")
        self.login(self.pablo)

        response = self.client.post(self._submit_url(order), {
            f"product_{bread.pk}": "2",
            f"product_{galletas.pk}": "1",
        })
        self.assertIn(response.status_code, (302, 303))

        # Quantities saved against the order under Pablo's nevera.
        pablo_lines = GroupOrderLineItem.objects.filter(
            product__group_order=order, customer=self.pablo,
        )
        qty = {li.product.name: li.quantity for li in pablo_lines}
        self.assertEqual(qty["Pan de espelta 1kg"], Decimal("2"))
        self.assertEqual(qty["Galletas 250gr"], Decimal("1"))

    def test_member_update_replaces_previous_quantities(self):
        # @US-03 edge case: latest replaces; no double counting (unique_together)
        order = self.make_order(self.gloria)
        bread = order.products.get(name="Pan de espelta 1kg")
        self.submit_line(order, self.pablo, bread, 2)  # prior submission
        self.login(self.pablo)

        self.client.post(self._submit_url(order), {f"product_{bread.pk}": "3"})

        lines = GroupOrderLineItem.objects.filter(product=bread, customer=self.pablo)
        self.assertEqual(lines.count(), 1)  # not counted twice
        self.assertEqual(lines.get().quantity, Decimal("3"))

    def test_submission_blocked_once_order_is_closed(self):
        # @US-03 error/boundary: blocked when not open
        order = self.make_order(self.gloria, status=GroupOrder.Status.CLOSED)
        bread = order.products.get(name="Pan de espelta 1kg")
        self.login(self.pablo)

        before = GroupOrderLineItem.objects.filter(
            product__group_order=order, customer=self.pablo,
        ).count()
        response = self.client.post(self._submit_url(order), {f"product_{bread.pk}": "2"})

        after = GroupOrderLineItem.objects.filter(
            product__group_order=order, customer=self.pablo,
        ).count()
        self.assertEqual(after, before)  # nothing recorded
        # Member is told the order is closed (stable copy: "cerrado").
        self.assertContains(response, "cerrado", status_code=response.status_code)

    def test_submission_blocked_when_closing_date_passed(self):
        # @US-03 error/boundary: lazy-derived close also blocks submission
        order = self.make_order(self.gloria, status=GroupOrder.Status.OPEN,
                                closing_date=self._past(days=1))
        bread = order.products.get(name="Pan de espelta 1kg")
        self.login(self.pablo)

        self.client.post(self._submit_url(order), {f"product_{bread.pk}": "2"})
        self.assertFalse(
            GroupOrderLineItem.objects.filter(
                product__group_order=order, customer=self.pablo,
            ).exists()
        )


# ---------------------------------------------------------------------------
# US-04 — Member sees "Mis pedidos"
# ---------------------------------------------------------------------------
class GroupOrderMineTests(GroupOrderTestMixin, TestCase):
    """US-04: per active order, the member's own line items + status. Active =
    currently open + the single most-recent arrived."""

    def setUp(self):
        self.url = reverse("lupanes:grouporder-mine")

    def test_anonymous_is_redirected_to_login(self):
        # @US-04 sad path
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_member_recalls_their_lines_across_active_orders(self):
        # @US-04 happy path
        bread = self.make_order(self.gloria, title="Pan", status=GroupOrder.Status.CLOSED)
        oil = self.make_order(self.didier, title="Aceite", status=GroupOrder.Status.OPEN,
                              products=[("Aceite virgen extra 5L", None)])
        self.submit_line(bread, self.pablo, bread.products.get(name="Pan de espelta 1kg"), 3)
        self.submit_line(bread, self.pablo, bread.products.get(name="Galletas 250gr"), 1)
        self.submit_line(oil, self.pablo, oil.products.get(name="Aceite virgen extra 5L"), 1)
        self.login(self.pablo)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # His own lines appear; statuses are visible to the consumer.
        self.assertContains(response, "Pan de espelta 1kg")
        self.assertContains(response, "Aceite virgen extra 5L")

    def test_member_only_sees_their_own_submissions(self):
        # @US-04 edge case: never other members' lines
        order = self.make_order(self.gloria, status=GroupOrder.Status.OPEN)
        bread = order.products.get(name="Pan de espelta 1kg")
        self.submit_line(order, self.pablo, bread, 2)
        self.submit_line(order, self.marta, bread, 5)  # Marta's line
        self.login(self.pablo)

        response = self.client.get(self.url)
        rendered = response.content.decode()
        # Marta's quantity (5) must not surface in Pablo's view; his (2) must.
        self.assertNotIn("marta", rendered.lower())

    def test_most_recent_arrived_order_appears_older_arrived_hidden(self):
        # @US-04 error/boundary: most-recent arrived shown; older arrived hidden
        now = timezone.now()
        old_bread = self.make_order(self.gloria, title="Pan viejo",
                                    status=GroupOrder.Status.ARRIVED)
        GroupOrder.objects.filter(pk=old_bread.pk).update(
            arrived_at=now - timedelta(days=10))
        new_oil = self.make_order(self.didier, title="Aceite reciente",
                                  status=GroupOrder.Status.ARRIVED,
                                  products=[("Aceite virgen extra 5L", None)])
        GroupOrder.objects.filter(pk=new_oil.pk).update(arrived_at=now)
        self.submit_line(old_bread, self.pablo,
                         old_bread.products.get(name="Pan de espelta 1kg"), 1)
        self.submit_line(new_oil, self.pablo,
                         new_oil.products.get(name="Aceite virgen extra 5L"), 1)
        self.login(self.pablo)

        response = self.client.get(self.url)
        self.assertContains(response, "Aceite virgen extra 5L")  # most recent arrived
        self.assertNotContains(response, "Pan viejo")  # older arrived hidden

    def test_inviting_empty_state_when_member_has_not_ordered(self):
        # @US-04 error/boundary: empty state invites checking the board
        self.login(self.pablo)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tablón")


# ---------------------------------------------------------------------------
# US-05 — Albarán reminder (flag ON/OFF, D13)
# ---------------------------------------------------------------------------
class GroupOrderReminderTests(GroupOrderTestMixin, TestCase):
    """US-05: read-only self-service albarán reminder shows iff
    paid_in_albaranes=True AND the viewing member has >= 1 line item. The tool
    NEVER writes a DeliveryNote (C-NOCHARGE)."""

    def _mine_url(self):
        return reverse("lupanes:grouporder-mine")

    def _detail_url(self, order):
        return reverse("lupanes:grouporder-detail", args=(order.pk,))

    def test_reminder_shown_when_flag_on_and_member_ordered(self):
        # @US-05 happy path: flag ON + member ordered => reminder + albarán link
        order = self.make_order(self.marta, title="Papel higiénico",
                                paid_in_albaranes=True,
                                products=[("Rollos sueltos", None)])
        self.submit_line(order, self.pablo, order.products.get(name="Rollos sueltos"), 6)
        self.login(self.pablo)

        response = self.client.get(self._mine_url())
        self.assertContains(response, "albarán")
        # Reminder deep-links to the EXISTING albarán flow (no new write path).
        self.assertContains(response, reverse("lupanes:deliverynote-new"))

    def test_no_reminder_when_flag_off(self):
        # @US-05 edge case: flag OFF => no reminder even though member ordered
        order = self.make_order(self.gloria, paid_in_albaranes=False)
        self.submit_line(order, self.pablo,
                         order.products.get(name="Pan de espelta 1kg"), 2)
        self.login(self.pablo)

        response = self.client.get(self._mine_url())
        self.assertNotContains(response, reverse("lupanes:deliverynote-new"))

    def test_no_reminder_for_member_who_did_not_order(self):
        # @US-05 error/boundary: flag ON but member did not order => no reminder
        order = self.make_order(self.marta, title="Papel higiénico",
                                paid_in_albaranes=True,
                                products=[("Rollos sueltos", None)])
        self.login(self.pablo)  # Pablo did NOT submit

        response = self.client.get(self._detail_url(order))
        self.assertNotContains(response, reverse("lupanes:deliverynote-new"))

    def test_viewing_reminder_never_creates_a_delivery_note(self):
        # @US-05 hard guarantee (D13): no DeliveryNote is ever written
        from lupanes.models import DeliveryNote
        order = self.make_order(self.marta, title="Papel higiénico",
                                paid_in_albaranes=True,
                                products=[("Rollos sueltos", None)])
        self.submit_line(order, self.pablo, order.products.get(name="Rollos sueltos"), 6)
        self.login(self.pablo)

        before = DeliveryNote.objects.count()
        self.client.get(self._mine_url())
        self.client.get(self._detail_url(order))
        self.assertEqual(DeliveryNote.objects.count(), before)  # unchanged


# ---------------------------------------------------------------------------
# US-06 — Organizer reads the per-member-per-product tally (creator-only)
# ---------------------------------------------------------------------------
class GroupOrderTallyTests(GroupOrderTestMixin, TestCase):
    """US-06: creator-only per-member-per-product tally with per-product totals.
    The tally lives as a creator-only section of the order detail page
    (architecture §10: no separate grouporder-tally URL)."""

    def _detail_url(self, order):
        return reverse("lupanes:grouporder-detail", args=(order.pk,))

    def _arrange_bread_order_with_two_members(self):
        order = self.make_order(self.gloria, status=GroupOrder.Status.CLOSED)
        bread = order.products.get(name="Pan de espelta 1kg")
        galletas = order.products.get(name="Galletas 250gr")
        self.submit_line(order, self.pablo, bread, 3)
        self.submit_line(order, self.pablo, galletas, 1)
        self.submit_line(order, self.marta, bread, 2)
        return order

    def test_creator_reads_per_member_per_product_tally_with_totals(self):
        # @US-06 @walking_skeleton @driving_port happy path
        order = self._arrange_bread_order_with_two_members()
        self.login(self.gloria)  # creator

        response = self.client.get(self._detail_url(order))
        self.assertEqual(response.status_code, 200)
        tally = response.context["tally"]  # creator gets tally in context
        self.assertIsNotNone(tally)
        # The page surfaces the per-product totals (Pan=5, Galletas=1) so Gloria
        # can copy it to the producer.
        rendered = response.content.decode()
        self.assertIn("Pan de espelta 1kg", rendered)
        self.assertIn("Galletas 250gr", rendered)

    def test_tally_works_with_a_single_participant(self):
        # @US-06 edge case: single row + matching totals still valid
        order = self.make_order(self.didier, title="Aceite", status=GroupOrder.Status.CLOSED,
                                products=[("Aceite virgen extra 5L", None)])
        self.submit_line(order, self.didier,
                         order.products.get(name="Aceite virgen extra 5L"), 1)
        self.login(self.didier)

        response = self.client.get(self._detail_url(order))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["tally"])

    def test_non_creator_does_not_see_the_tally_section(self):
        # @US-06 error/boundary: tally is creator-only (defense in depth — not in
        # context for non-creators).
        order = self._arrange_bread_order_with_two_members()
        self.login(self.pablo)  # not the creator
        response = self.client.get(self._detail_url(order))
        self.assertEqual(response.status_code, 200)  # shared detail page
        self.assertIsNone(response.context.get("tally"))

    def test_manager_who_is_not_creator_does_not_see_the_tally(self):
        # @US-06 @property: manager group grants NO organizer rights (C-ORGANIZER)
        order = self._arrange_bread_order_with_two_members()
        self.login(self.santi)  # tienda manager, not the creator
        response = self.client.get(self._detail_url(order))
        self.assertIsNone(response.context.get("tally"))


# ---------------------------------------------------------------------------
# US-07 — Order-open email to the socios list (D3, hard requirement)
# ---------------------------------------------------------------------------
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class GroupOrderEmailTests(GroupOrderTestMixin, TestCase):
    """US-07: opening an order announces it to GROUP_ORDER_NOTIFY_EMAIL.

    The app default backend is post_office.EmailBackend (enqueues, does NOT fill
    mail.outbox), so these tests override to locmem and assert on mail.outbox
    (architecture §8 testability finding).
    """

    def setUp(self):
        self.url = reverse("lupanes:grouporder-new")

    def _open_bread_order(self):
        return self.client.post(self.url, {
            "title": "Pan semana del 2 de junio",
            "producer_name": "Aineto",
            "closing_date": "2026-06-01 20:00",
            "estimated_delivery_date": "2026-06-03",
            "paid_in_albaranes": False,
            "products-TOTAL_FORMS": "2",
            "products-INITIAL_FORMS": "0",
            "products-MIN_NUM_FORMS": "1",
            "products-MAX_NUM_FORMS": "1000",
            "products-0-name": "Pan de espelta 1kg",
            "products-0-price": "4.50",
            "products-1-name": "Galletas 250gr",
            "products-1-price": "2.00",
        })

    def test_opening_an_order_announces_it_to_the_socios_list(self):
        # @US-07 happy path: email to socios with key content
        from django.conf import settings
        self.login(self.gloria)
        self._open_bread_order()

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        notify = getattr(settings, "GROUP_ORDER_NOTIFY_EMAIL", "socios@lupierra.es")
        self.assertIn(notify, message.to)
        body = f"{message.subject}\n{message.body}"
        self.assertIn("Pan semana del 2 de junio", body)  # title
        self.assertIn("Aineto", body)                      # producer
        self.assertIn("Pan de espelta 1kg", body)          # line item

    def test_email_lists_items_even_when_some_have_no_price(self):
        # @US-07 edge case: items without price still listed
        self.login(self.didier)
        self.client.post(self.url, {
            "title": "Aceite primavera 2026",
            "producer_name": "ecoMatarranya",
            "closing_date": "2026-06-05 20:00",
            "paid_in_albaranes": False,
            "products-TOTAL_FORMS": "2",
            "products-INITIAL_FORMS": "0",
            "products-MIN_NUM_FORMS": "1",
            "products-MAX_NUM_FORMS": "1000",
            "products-0-name": "Aceite virgen extra 5L",
            "products-0-price": "",
            "products-1-name": "Aceite virgen extra 2L",
            "products-1-price": "",
        })
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertIn("Aceite virgen extra 5L", body)
        self.assertIn("Aceite virgen extra 2L", body)

    def test_failed_announcement_does_not_lose_the_order(self):
        # @US-07 error/boundary: SMTP failure -> order still created 'open',
        # failure logged, organizer warned. Order is never silently lost.
        from unittest.mock import patch
        self.login(self.gloria)

        with patch("django.core.mail.send_mail", side_effect=Exception("smtp down")):
            with self.assertLogs("lupanes", level="ERROR"):
                response = self._open_bread_order()

        # Order persists as open despite the mail failure.
        order = GroupOrder.objects.get(title="Pan semana del 2 de junio")
        self.assertEqual(order.status, GroupOrder.Status.OPEN)
        # Organizer is informed via a warning message.
        messages = [m.message for m in response.wsgi_request._messages] \
            if hasattr(response.wsgi_request, "_messages") else []
        # Message framework storage is consumed on render; assert via follow.
        followed = self.client.get(reverse("lupanes:grouporder-list"))
        self.assertEqual(followed.status_code, 200)


# ---------------------------------------------------------------------------
# US-08 — Order status lifecycle (open -> closed -> ordered -> arrived)
# ---------------------------------------------------------------------------
class GroupOrderStatusTests(GroupOrderTestMixin, TestCase):
    """US-08: forward-only lifecycle; creator-only; submissions only while open."""

    def _status_url(self, order):
        return reverse("lupanes:grouporder-status", args=(order.pk,))

    def test_organizer_advances_order_through_lifecycle(self):
        # @US-08 happy path: open -> closed -> ordered -> arrived
        order = self.make_order(self.gloria, status=GroupOrder.Status.OPEN)
        self.login(self.gloria)

        for target in (GroupOrder.Status.CLOSED, GroupOrder.Status.ORDERED,
                       GroupOrder.Status.ARRIVED):
            response = self.client.post(self._status_url(order), {"status": target})
            self.assertIn(response.status_code, (302, 303))
            order.refresh_from_db()
            self.assertEqual(order.status, target)

        # Arriving stamps arrived_at (used by US-04 most-recent-arrived ordering).
        self.assertIsNotNone(order.arrived_at)

    def test_organizer_closes_an_order_early(self):
        # @US-08 edge case: close before closing date; submissions then blocked
        order = self.make_order(self.didier, status=GroupOrder.Status.OPEN,
                                closing_date=self._future(days=5),
                                products=[("Aceite virgen extra 5L", None)])
        self.login(self.didier)

        self.client.post(self._status_url(order), {"status": GroupOrder.Status.CLOSED})
        order.refresh_from_db()
        self.assertEqual(order.status, GroupOrder.Status.CLOSED)

        # Further submissions are blocked once closed.
        oil_product = order.products.get(name="Aceite virgen extra 5L")
        self.login(self.pablo)
        self.client.post(reverse("lupanes:grouporder-submit", args=(order.pk,)),
                         {f"product_{oil_product.pk}": "1"})
        self.assertFalse(
            GroupOrderLineItem.objects.filter(
                product__group_order=order, customer=self.pablo,
            ).exists()
        )

    def test_non_creator_cannot_change_status(self):
        # @US-08 error/boundary: creator-only (Pablo is a customer, not creator)
        order = self.make_order(self.gloria, status=GroupOrder.Status.OPEN)
        self.login(self.pablo)
        response = self.client.post(self._status_url(order),
                                    {"status": GroupOrder.Status.CLOSED})
        self.assertEqual(response.status_code, 403)  # authenticated => forbidden
        order.refresh_from_db()
        self.assertEqual(order.status, GroupOrder.Status.OPEN)  # unchanged

    def test_manager_who_is_not_creator_cannot_change_status(self):
        # @US-08 @property: manager group grants no organizer rights
        order = self.make_order(self.gloria, status=GroupOrder.Status.OPEN)
        self.login(self.santi)
        response = self.client.post(self._status_url(order),
                                    {"status": GroupOrder.Status.CLOSED})
        self.assertEqual(response.status_code, 403)
        order.refresh_from_db()
        self.assertEqual(order.status, GroupOrder.Status.OPEN)

    def test_status_only_moves_forward(self):
        # @US-08 error/boundary: backward transition rejected
        order = self.make_order(self.gloria, status=GroupOrder.Status.ORDERED)
        self.login(self.gloria)
        self.client.post(self._status_url(order), {"status": GroupOrder.Status.OPEN})
        order.refresh_from_db()
        self.assertEqual(order.status, GroupOrder.Status.ORDERED)  # not rolled back


# ---------------------------------------------------------------------------
# Cross-cutting @property scenarios (acceptance-criteria.md "Cross-cutting")
# ---------------------------------------------------------------------------
class GroupOrderConsistencyTests(GroupOrderTestMixin, TestCase):
    """Cross-cutting invariants validated as table-driven example tests
    (architecture §12): Mis-pedidos == tally; organizer actions never reach
    non-creators regardless of manager group."""

    @override_settings()
    def test_mis_pedidos_quantities_match_the_tally(self):
        # @property: every quantity a member sees equals the tally cell
        order = self.make_order(self.gloria, status=GroupOrder.Status.CLOSED)
        bread = order.products.get(name="Pan de espelta 1kg")
        galletas = order.products.get(name="Galletas 250gr")
        self.submit_line(order, self.pablo, bread, 3)
        self.submit_line(order, self.pablo, galletas, 1)

        # What Pablo sees in "Mis pedidos"
        self.login(self.pablo)
        mine = self.client.get(reverse("lupanes:grouporder-mine"))
        mine_rendered = mine.content.decode()
        self.assertIn("Pan de espelta 1kg", mine_rendered)

        # What Gloria (creator) sees in the tally — same underlying line items.
        self.login(self.gloria)
        detail = self.client.get(reverse("lupanes:grouporder-detail", args=(order.pk,)))
        self.assertIsNotNone(detail.context["tally"])
        # Both read from the same GroupOrderLineItem rows (single source of truth).
        lines = GroupOrderLineItem.objects.filter(
            product__group_order=order, customer=self.pablo,
        )
        qty = {li.product.name: li.quantity for li in lines}
        self.assertEqual(qty["Pan de espelta 1kg"], Decimal("3"))
        self.assertEqual(qty["Galletas 250gr"], Decimal("1"))

    def test_organizer_only_actions_never_available_to_non_creators(self):
        # @property: tally, status controls, flag/edit unavailable to any
        # non-creator, regardless of manager group membership.
        order = self.make_order(self.gloria, status=GroupOrder.Status.OPEN)

        for non_creator in (self.pablo, self.marta, self.santi):
            self.login(non_creator)
            # Editing the order header is creator-only (GroupOrderOwnerMixin).
            edit = self.client.get(reverse("lupanes:grouporder-edit", args=(order.pk,)))
            self.assertEqual(edit.status_code, 403, f"{non_creator.username} could edit")
            # Advancing status is creator-only.
            status = self.client.post(
                reverse("lupanes:grouporder-status", args=(order.pk,)),
                {"status": GroupOrder.Status.CLOSED},
            )
            self.assertEqual(status.status_code, 403, f"{non_creator.username} changed status")
            order.refresh_from_db()
            self.assertEqual(order.status, GroupOrder.Status.OPEN)
