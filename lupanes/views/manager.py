from decimal import Decimal
from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils import timezone
from django.views.generic import ListView, RedirectView
from django.views.generic.dates import MonthArchiveView
from django.urls import reverse

from lupanes import helpers
from lupanes.models import DeliveryNote
from lupanes.users.mixins import ManagerAuthMixin

User = get_user_model()


# TODO: move to users module???
class CustomerListView(ManagerAuthMixin, ListView):
    template_name = "users/user_list.html"
    model = User

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.filter(is_active=True, groups__name="neveras")


class DeliveryNoteCurrentMonthArchiveView(ManagerAuthMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        now = timezone.now()
        return reverse("lupanes:deliverynote-month", args=(now.year, now.month))


class DeliveryNoteMonthArchiveView(ManagerAuthMixin, MonthArchiveView):
    queryset = DeliveryNote.objects.all()
    date_field = "date"
    allow_empty = True


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
