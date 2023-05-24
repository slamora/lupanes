from typing import Any, Dict

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from lupanes.models import Customer


class CustomerAuthMixin:
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        customer_id = self.request.session.get("customer_id")
        try:
            self.customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context
