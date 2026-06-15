import logging
from decimal import Decimal
from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from lupanes.forms import GroupOrderForm, GroupOrderProductFormSet
from lupanes.models import GroupOrder, GroupOrderLineItem
from lupanes.users.mixins import CustomerAuthMixin

logger = logging.getLogger(__name__)


def send_group_order_announcement(order, request=None):
    """Announce a freshly opened order to the socios list (D3)."""
    recipient = settings.GROUP_ORDER_NOTIFY_EMAIL
    subject = f"Se abre pedido: {order.title}"
    body = render_to_string(
        "emails/grouporder_announcement.txt", {"order": order}, request=request,
    )
    mail.send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)


def build_tally(order):
    """Per-member-per-product quantities + per-product totals for the organizer."""
    products = list(order.products.all())
    line_items = (
        GroupOrderLineItem.objects
        .filter(product__group_order=order)
        .select_related("product", "customer")
    )
    by_customer: Dict[Any, Dict[int, Decimal]] = {}
    totals: Dict[int, Decimal] = {p.id: Decimal("0") for p in products}
    for li in line_items:
        by_customer.setdefault(li.customer, {})[li.product_id] = li.quantity
        totals[li.product_id] = totals.get(li.product_id, Decimal("0")) + li.quantity
    rows = [
        {"customer": customer, "quantities": [qtys.get(p.id) for p in products]}
        for customer, qtys in by_customer.items()
    ]
    return {
        "products": products,
        "rows": rows,
        "totals": [totals.get(p.id, Decimal("0")) for p in products],
    }


class GroupOrderListView(CustomerAuthMixin, ListView):
    """US-02: board of currently-open orders (lazy-derived close)."""
    template_name = "lupanes/grouporder_list.html"

    def get_queryset(self):
        return GroupOrder.objects.filter(
            status=GroupOrder.Status.OPEN, closing_date__gt=timezone.now(),
        )


class GroupOrderCreateView(CustomerAuthMixin, CreateView):
    """US-01: an organizer opens a group order with freeform line items."""
    model = GroupOrder
    form_class = GroupOrderForm
    template_name = "lupanes/grouporder_form.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if "product_formset" not in context:
            data = self.request.POST if self.request.method == "POST" else None
            context["product_formset"] = GroupOrderProductFormSet(data, prefix="products")
        return context

    def form_valid(self, form):
        formset = GroupOrderProductFormSet(self.request.POST, prefix="products")
        if not formset.is_valid():
            return self.form_invalid(form, product_formset=formset)

        form.instance.created_by = self.request.user
        form.instance.status = GroupOrder.Status.OPEN
        self.object = form.save()
        formset.instance = self.object
        formset.save()

        self._announce(self.object)
        return redirect("lupanes:grouporder-detail", pk=self.object.pk)

    def form_invalid(self, form, product_formset=None):
        context = self.get_context_data(form=form)
        if product_formset is not None:
            context["product_formset"] = product_formset
        return self.render_to_response(context)

    def _announce(self, order):
        try:
            send_group_order_announcement(order, self.request)
            messages.success(self.request, "Pedido abierto. Se ha avisado a los socios por email.")
        except Exception as e:
            logger.error(f"No se pudo enviar el aviso del pedido {order.pk}: {e}")
            messages.warning(
                self.request,
                "El pedido se ha abierto, pero no se pudo enviar el aviso por email a los socios.",
            )


class GroupOrderDetailView(LoginRequiredMixin, DetailView):
    """US-03 surface / US-05 reminder / US-06 creator-only tally.

    Viewable by any authenticated member; the tally section is creator-only.
    """
    model = GroupOrder
    template_name = "lupanes/grouporder_detail.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order = self.object
        user = self.request.user

        my_lines = GroupOrderLineItem.objects.filter(
            product__group_order=order, customer=user,
        ).select_related("product")
        context["my_lines"] = my_lines
        context["my_quantities"] = {li.product_id: li.quantity for li in my_lines}

        is_creator = order.created_by_id == user.id
        context["is_creator"] = is_creator
        context["tally"] = build_tally(order) if is_creator else None
        context["show_albaran_reminder"] = order.paid_in_albaranes and my_lines.exists()
        return context
