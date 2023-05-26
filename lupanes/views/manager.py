import calendar
from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils import timezone
from django.views.generic import ListView

from lupanes import helpers
from lupanes.models import DeliveryNote
from lupanes.users.mixins import ManagerAuthMixin

User = get_user_model()


class DeliveryNoteListView(ManagerAuthMixin, ListView):
    model = DeliveryNote

    def get_queryset(self) -> QuerySet[Any]:
        value = self.request.GET.get("month")
        self.month = helpers.clean_month(value)

        return DeliveryNote.objects.filter(
            date__date__year=self.month.year,
            date__date__month=self.month.month,
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        choices = {
            i: calendar.month_name[i]
            for i in range(1, today.month + 1)
        }

        context.update({
            "month": self.month,
            "choices": choices,
        })
        return context


class DeliveryNoteSummaryView(ManagerAuthMixin, ListView):
    template_name = "lupanes/deliverynote_summary.html"

    def get_queryset(self) -> QuerySet[Any]:
        value = self.request.GET.get("month")
        self.period = helpers.clean_month(value)

        qs = User.objects.filter(is_active=True)
        for customer in qs:
            customer.total = Decimal(0)
            notes = customer.deliverynote_set.filter(
                date__date__year=self.period.year,
                date__date__month=self.period.month,
            )
            for note in notes:
                customer.total += note.amount()

        return qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["period"] = self.period
        return context
