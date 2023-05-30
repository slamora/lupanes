from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms.models import BaseModelForm
from django.http import (HttpRequest, HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.html import mark_safe
from django.views.generic import DetailView, ListView, RedirectView
from django.views.generic.dates import MonthArchiveView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from lupanes.forms import DeliveryNoteCreateForm, ProductPriceForm
from lupanes.models import DeliveryNote, Product
from lupanes.users.mixins import CustomerAuthMixin

User = get_user_model()


class DeliveryNoteCreateView(CustomerAuthMixin, CreateView):
    form_class = DeliveryNoteCreateForm
    model = DeliveryNote
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["customer"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["deliverynotes_today"] = DeliveryNote.objects.filter(
            customer=self.request.user, date__date=today,
        )
        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        msg = mark_safe("Albarán registrado correctamente. Si lo necesitas, tienes "
                        "<strong>hasta el final del día</strong> para editarlo o borrarlo.")
        messages.success(self.request, _(msg))
        return super().form_valid(form)


class DeliveryNoteUpdateView(CustomerAuthMixin, UpdateView):
    model = DeliveryNote
    fields = ["product", "quantity"]
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def get_queryset(self) -> QuerySet[Any]:
        today = timezone.now().date()
        return DeliveryNote.objects.filter(customer=self.request.user, date__date=today)


class DeliveryNoteDeleteView(CustomerAuthMixin, DeleteView):
    model = DeliveryNote
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def get_queryset(self) -> QuerySet[Any]:
        today = timezone.now().date()
        return DeliveryNote.objects.filter(customer=self.request.user, date__date=today)


class CustomerDeliveryNoteCurrentMonthArchiveView(CustomerAuthMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        now = timezone.now()
        return reverse("lupanes:deliverynote-month-customer", args=(now.year, now.month))


class CustomerDeliveryNoteMonthArchiveView(CustomerAuthMixin, MonthArchiveView):
    template_name = "lupanes/my_deliverynote_archive_month.html"
    queryset = DeliveryNote.objects.all()
    date_field = "date"
    allow_empty = True

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        return qs.filter(customer=self.request.user)


class ProductAjaxView(CustomerAuthMixin, DetailView):
    model = Product

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        obj = self.get_object()
        data = {
            "pk": obj.pk,
            "name": obj.name,
            "price": obj.get_price_on(),
            "unit": {
                "name": obj.unit,
                "accept_decimals": obj.unit_accept_decimals(),
            }
        }
        return JsonResponse(data=data)


class ProductListView(CustomerAuthMixin, ListView):
    model = Product


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ["name"]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form_pprice"] = ProductPriceForm(product=self.object)
        return context

    def get_success_url(self) -> str:
        return reverse("lupanes:product-edit", args=(self.kwargs["pk"],))


class ProductNewPriceView(LoginRequiredMixin, CreateView):
    form_class = ProductPriceForm

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["product"] = get_object_or_404(Product, pk=self.kwargs["pk"])
        return kwargs

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        # TODO(@slamora): return `ProductUpdateView.form_invalid` response
        messages.error(self.request, form.errors)
        return HttpResponseRedirect(redirect_to=self.get_success_url())

    def get_success_url(self) -> str:
        return reverse("lupanes:product-edit", args=(self.kwargs["pk"],))
