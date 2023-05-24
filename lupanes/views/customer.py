from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import QuerySet
from django.forms.models import BaseModelForm
from django.http import (HttpRequest, HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, RedirectView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)

from lupanes.forms import (CustomerAuthForm, DeliveryNoteCreateForm,
                           ProductPriceForm)
from lupanes.mixins import CustomerAuthMixin
from lupanes.models import DeliveryNote, Product


class CustomerLoginView(FormView):
    form_class = CustomerAuthForm
    template_name = "lupanes/customer_login.html"
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def form_valid(self, form: Any) -> HttpResponse:
        self.request.session["customer_id"] = form.customer_id
        return super().form_valid(form)


class CustomerLogoutView(RedirectView):
    pattern_name = "lupanes:customer-login"

    def get_redirect_url(self, *args, **kwargs):
        try:
            del self.request.session["customer_id"]
        except KeyError:
            pass
        return super().get_redirect_url(*args, **kwargs)


class DeliveryNoteCreateView(CustomerAuthMixin, CreateView):
    form_class = DeliveryNoteCreateForm
    model = DeliveryNote
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["customer"] = self.customer
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["deliverynotes_today"] = DeliveryNote.objects.filter(
            customer=self.customer, date__date=today,
        )
        return context


class DeliveryNoteUpdateView(CustomerAuthMixin, UpdateView):
    model = DeliveryNote
    fields = ["product", "quantity"]
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def get_queryset(self) -> QuerySet[Any]:
        today = timezone.now().date()
        return DeliveryNote.objects.filter(customer=self.customer, date__date=today)


class DeliveryNoteDeleteView(CustomerAuthMixin, DeleteView):
    model = DeliveryNote
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def get_queryset(self) -> QuerySet[Any]:
        today = timezone.now().date()
        return DeliveryNote.objects.filter(customer=self.customer, date__date=today)


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
