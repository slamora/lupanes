from typing import Any, Dict

from django.contrib import messages
from django.forms.models import BaseModelForm
from django.http import (HttpRequest, HttpResponse, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from lupanes.forms import ProductPriceForm
from lupanes.models import Product
from lupanes.users.mixins import CustomerAuthMixin, ManagerAuthMixin


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


class ProductUpdateView(ManagerAuthMixin, UpdateView):
    model = Product
    fields = ["name"]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form_pprice"] = ProductPriceForm(product=self.object)
        return context

    def get_success_url(self) -> str:
        return reverse("lupanes:product-edit", args=(self.kwargs["pk"],))


class ProductNewPriceView(ManagerAuthMixin, CreateView):
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
