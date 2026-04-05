import datetime
import urllib
from decimal import Decimal
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Sum
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.formats import date_format
from django.views.generic import (CreateView, DeleteView, ListView,
                                  RedirectView, UpdateView)
from django.views.generic.dates import MonthArchiveView, MonthMixin, YearMixin

from lupanes.exceptions import PriceDoesNotExistOnDate
from lupanes.forms import DeliveryNoteForm
from lupanes.models import DeliveryNote, Product
from lupanes.users.mixins import ManagerAuthMixin

User = get_user_model()


# TODO: move to users module???
class CustomerListView(ManagerAuthMixin, ListView):
    template_name = "users/user_list.html"
    model = User

    def get_queryset(self) -> QuerySet[User]:
        return self.model.objects.get_active_customers()


class DeliveryNoteCurrentMonthArchiveView(ManagerAuthMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        now = timezone.now()
        return reverse("lupanes:deliverynote-month", args=(now.year, now.month))


class DeliveryNoteMonthArchiveView(ManagerAuthMixin, MonthArchiveView):
    queryset = DeliveryNote.objects.all()
    date_field = "date"
    ordering = "date"
    allow_empty = True


class DeliveryNoteSummaryView(ManagerAuthMixin, YearMixin, MonthMixin, ListView):
    template_name = "lupanes/deliverynote_summary.html"
    date_field = "date"

    def get_queryset(self) -> QuerySet[Any]:
        year = self.kwargs["year"]
        month = self.kwargs["month"]
        self.period = datetime.datetime(year=year, month=month, day=1)

        qs = User.objects.get_active_customers()
        for customer in qs:
            customer.total = Decimal(0)
            notes = customer.deliverynote_set.filter(
                date__date__year=year,
                date__date__month=month,
            )
            for note in notes:
                try:
                    customer.total += note.amount()
                except PriceDoesNotExistOnDate as e:
                    messages.error(self.request, e)
                    customer.total = None
                    break

            if customer.total is not None:
                customer.total_export_format = '{0:.2f}'.format(customer.total)

        return qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["period"] = self.period
        return context


class DeliveryNoteBulkCreateView(ManagerAuthMixin, CreateView):
    form_class = DeliveryNoteForm
    template_name = "lupanes/deliverynote_bulk_create.html"

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {
            'customer': self.request.GET.get("customer"),
            'date': self.request.GET.get("date"),
        }
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self) -> str:
        messages.success(self.request, "Albarán creado correctamente.")

        date = self.request.POST["date"]
        on_success = self.request.POST.get("on-success")
        params = {}
        if on_success == "new-same-customer":
            params = {
                "date": date,
                "customer": self.request.POST["customer"]
            }
        elif on_success == "new-another-customer":
            params = {
                "date": date,
            }
        elif on_success == "go-back-to-list":
            return reverse_lazy("lupanes:deliverynote-current-month")

        return "{}?{}".format(
            reverse_lazy("lupanes:deliverynote-new-bulk"),
            urllib.parse.urlencode(params)
        )


class DeliveryNoteBulkUpdateView(ManagerAuthMixin, UpdateView):
    form_class = DeliveryNoteForm
    template_name = "lupanes/deliverynote_bulk_create.html"
    model = DeliveryNote

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self) -> str:
        date = self.object.date
        note_date = date_format(date, format='SHORT_DATE_FORMAT', use_l10n=True)
        msg = (f"Albarán con fecha { note_date } de { self.object.customer.username } "
               f"y producto {self.object.product.name} actualizado correctamente.")
        messages.info(self.request, msg)

        return reverse_lazy("lupanes:deliverynote-month", args=(date.year, date.month))


class DeliveryNoteBulkDeleteView(ManagerAuthMixin, DeleteView):
    model = DeliveryNote
    template_name = "lupanes/deliverynote_bulk_confirm_delete.html"

    def get_success_url(self) -> str:
        date = self.object.date
        messages.info(self.request, "Albarán borrado correctamente.")
        return reverse_lazy("lupanes:deliverynote-month", args=(date.year, date.month))


class ProductSummaryView(ManagerAuthMixin, ListView):
    template_name = "lupanes/product_summary.html"
    context_object_name = "product_summary"

    def _has_invalid_date_range(self):
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        return date_from and date_to and date_from > date_to

    def get_queryset(self):
        if self._has_invalid_date_range():
            return []

        qs = DeliveryNote.objects.select_related("product", "product__producer").all()

        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        products = self.request.GET.getlist("products")

        if date_from:
            qs = qs.filter(date__date__gte=date_from)
        if date_to:
            qs = qs.filter(date__date__lte=date_to)
        if products:
            qs = qs.filter(product__pk__in=products)

        summary = qs.values(
            "product__name", "product__producer__name", "product__unit"
        ).annotate(
            total_qty=Sum("quantity"),
        ).order_by("product__name")

        # Calculate total_amount per product using Python (price depends on note date)
        for item in summary:
            product_notes = qs.filter(product__name=item["product__name"])
            total_amount = Decimal("0")
            for note in product_notes:
                try:
                    total_amount += note.amount()
                except PriceDoesNotExistOnDate:
                    pass
            item["total_amount"] = total_amount

        return summary

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(is_active=True).select_related("producer").order_by("name")
        context["selected_products"] = [
            int(pk) for pk in self.request.GET.getlist("products") if pk
        ]
        context["date_from"] = self.request.GET.get("date_from", "")
        context["date_to"] = self.request.GET.get("date_to", "")
        context["invalid_date_range"] = self._has_invalid_date_range()

        summary = context["product_summary"]
        total_amount = sum(
            (item["total_amount"] for item in summary), Decimal("0")
        )
        total_qty = sum(
            (item["total_qty"] for item in summary), Decimal("0")
        )
        context["totals"] = {
            "total_amount": total_amount,
            "total_qty": total_qty,
        }
        return context
