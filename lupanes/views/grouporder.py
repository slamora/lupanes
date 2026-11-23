import logging
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

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


class GroupOrderOwnerMixin(UserPassesTestMixin):
    """Creator-gated access. NOT manager-gated: the tienda group grants no rights.

    Authenticated non-creators get 403; anonymous users are redirected to login.
    """

    def get_group_order(self):
        if not hasattr(self, "_group_order"):
            self._group_order = get_object_or_404(GroupOrder, pk=self.kwargs["pk"])
        return self._group_order

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and self.get_group_order().created_by_id == user.id


def order_view_context(order, user):
    """Context shared by the order detail page and the submission flow."""
    my_lines = (
        GroupOrderLineItem.objects
        .filter(product__group_order=order, customer=user)
        .select_related("product")
    )
    my_quantities = {li.product_id: li.quantity for li in my_lines}
    product_rows = [
        {"product": p, "my_qty": my_quantities.get(p.id)}
        for p in order.products.all()
    ]
    is_creator = order.created_by_id == user.id
    return {
        "my_lines": my_lines,
        "my_quantities": my_quantities,
        "product_rows": product_rows,
        "is_creator": is_creator,
        "tally": build_tally(order) if is_creator else None,
        "show_albaran_reminder": order.paid_in_albaranes and my_lines.exists(),
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
        context.update(order_view_context(self.object, self.request.user))
        return context


class GroupOrderSubmitView(CustomerAuthMixin, View):
    """US-03: a member submits/updates quantities while the order is open."""

    def get(self, request, pk):
        return redirect("lupanes:grouporder-detail", pk=pk)

    def post(self, request, pk):
        order = get_object_or_404(GroupOrder, pk=pk)
        if not order.is_open():
            context = {
                "object": order,
                "submit_error": "Este pedido está cerrado, ya no se pueden añadir productos.",
            }
            context.update(order_view_context(order, request.user))
            return render(request, "lupanes/grouporder_detail.html", context)

        for product in order.products.all():
            raw = request.POST.get(f"product_{product.pk}", "").strip()
            if raw == "":
                continue
            try:
                quantity = Decimal(raw)
            except (InvalidOperation, ValueError):
                continue
            if quantity > 0:
                GroupOrderLineItem.objects.update_or_create(
                    product=product, customer=request.user,
                    defaults={"quantity": quantity},
                )
            else:
                GroupOrderLineItem.objects.filter(
                    product=product, customer=request.user,
                ).delete()
        messages.success(request, "Hemos guardado tu pedido. ¡Gracias!")
        return redirect("lupanes:grouporder-mine")


class GroupOrderMineView(CustomerAuthMixin, TemplateView):
    """US-04: the member's own line items across active orders.

    Active = open / closed / ordered, plus the single most-recent arrived order.
    """
    template_name = "lupanes/grouporder_mine.html"

    _ACTIVE_STATES = (
        GroupOrder.Status.OPEN, GroupOrder.Status.CLOSED, GroupOrder.Status.ORDERED,
    )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user

        lines_by_order: Dict[Any, list] = {}
        line_items = (
            GroupOrderLineItem.objects
            .filter(customer=user)
            .select_related("product", "product__group_order")
        )
        for li in line_items:
            lines_by_order.setdefault(li.product.group_order, []).append(li)

        most_recent_arrived = (
            GroupOrder.objects
            .filter(status=GroupOrder.Status.ARRIVED, products__line_items__customer=user)
            .order_by("-arrived_at")
            .first()
        )

        items = []
        for order, lines in lines_by_order.items():
            is_active = order.status in self._ACTIVE_STATES
            is_latest_arrived = (
                most_recent_arrived is not None and order.pk == most_recent_arrived.pk
            )
            if is_active or is_latest_arrived:
                items.append({
                    "order": order,
                    "lines": lines,
                    "show_albaran_reminder": order.paid_in_albaranes,
                })
        items.sort(key=lambda d: d["order"].created_at, reverse=True)
        context["order_items"] = items
        return context


class GroupOrderStatusView(GroupOrderOwnerMixin, View):
    """US-08: creator advances the order forward (open → closed → ordered → arrived)."""

    def get(self, request, pk):
        return redirect("lupanes:grouporder-detail", pk=pk)

    def post(self, request, pk):
        order = self.get_group_order()
        target = request.POST.get("status")
        if order.can_advance_to(target):
            order.status = target
            if target == GroupOrder.Status.ARRIVED:
                order.arrived_at = timezone.now()
            order.save()
            messages.success(request, "Estado del pedido actualizado.")
        else:
            messages.warning(request, "Ese cambio de estado no está permitido.")
        return redirect("lupanes:grouporder-detail", pk=order.pk)


class GroupOrderEditView(GroupOrderOwnerMixin, UpdateView):
    """US-01/US-08: creator edits the order header and its products."""
    model = GroupOrder
    form_class = GroupOrderForm
    template_name = "lupanes/grouporder_form.html"

    def get_object(self, queryset=None):
        return self.get_group_order()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if "product_formset" not in context:
            data = self.request.POST if self.request.method == "POST" else None
            context["product_formset"] = GroupOrderProductFormSet(
                data, instance=self.object, prefix="products",
            )
        return context

    def form_valid(self, form):
        formset = GroupOrderProductFormSet(
            self.request.POST, instance=self.object, prefix="products",
        )
        if not formset.is_valid():
            return self.form_invalid(form, product_formset=formset)
        self.object = form.save()
        formset.save()
        messages.success(self.request, "Pedido actualizado.")
        return redirect("lupanes:grouporder-detail", pk=self.object.pk)

    def form_invalid(self, form, product_formset=None):
        context = self.get_context_data(form=form)
        if product_formset is not None:
            context["product_formset"] = product_formset
        return self.render_to_response(context)
