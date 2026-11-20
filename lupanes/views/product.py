from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from lupanes.filters import ProductFilter
from lupanes.forms import ProductForm, ProductPriceForm
from lupanes.models import Producer, Product
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
            },
        }
        return JsonResponse(data=data)


class ProductListView(LoginRequiredMixin, ListView):
    model = Product

    def get_filter(self) -> ProductFilter:
        if not hasattr(self, "_filter"):
            self._filter = ProductFilter(self.request.GET, self.request.user)
        return self._filter

    def get_queryset(self) -> QuerySet[Product]:
        return self.get_filter().filter_queryset(super().get_queryset())

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        filter_obj = self.get_filter()

        context.update(
            {
                "search_query": filter_obj.search_query,
                "producers": Producer.objects.filter(
                    pk__in=filter_obj.visible_producer_ids
                ).order_by(Lower("name")),
                "selected_producer": filter_obj.selected_producer,
                "selected_unit": filter_obj.selected_unit,
                "selected_active": filter_obj.selected_active,
                "selected_sort": filter_obj.selected_sort,
                "sort_urls": filter_obj.get_sort_urls(),
                "unit_choices": Product.Unit.choices,
                "can_filter_status": filter_obj.can_filter_status,
            }
        )
        return context


class ProductCreateView(ManagerAuthMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "lupanes/product_create.html"

    def get_success_url(self) -> str:
        messages.info(
            self.request,
            "Para continuar la creación del producto, introduce su precio.",
        )
        return reverse("lupanes:product-edit", args=(self.object.pk,))


class ProductUpdateView(ManagerAuthMixin, UpdateView):
    model = Product
    form_class = ProductForm

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form_pprice"] = ProductPriceForm(product=self.object)
        return context

    def get_success_url(self) -> str:
        messages.success(self.request, "Producto actualizado correctamente.")
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
