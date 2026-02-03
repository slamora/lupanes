import logging
from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import mail_managers, send_mail
from django.db.models import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from django.views.generic import FormView, RedirectView, TemplateView
from django.views.generic.dates import MonthArchiveView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from gspread.exceptions import APIError

from lupanes.forms import DeliveryNoteCreateForm, NotifyMissingProductForm
from lupanes.models import DeliveryNote
from lupanes.users.mixins import CustomerAuthMixin

logger = logging.getLogger(__name__)
User = get_user_model()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "lupanes/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        try:
            context["balance"] = self.request.user.current_balance
            context["consumption"] = self.request.user.current_month_consumption()
            context["projected_balance"] = self.request.user.projected_balance()
        except APIError as e:
            logger.error(f"Cannot fetch nevera balance: {e}")
            messages.warning(self.request, "Fallo temporal, error al obtener tu saldo.")
            context["balance"] = "N/A"
            context["consumption"] = None
            context["projected_balance"] = None

        return context


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
        qs = self.model.objects.filter(
            customer=self.request.user, date__date=today,
        )
        total = sum(note.amount() for note in qs)
        context.update({
            "deliverynotes_today": qs,
            "total_amount": total,
        })
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


class NotifyMissingProductView(CustomerAuthMixin, FormView):
    form_class = NotifyMissingProductForm
    template_name = "lupanes/deliverynote_notify_missing_product.html"
    success_url = reverse_lazy("lupanes:deliverynote-new")

    def form_valid(self, form: Any) -> HttpResponse:
        response = super().form_valid(form)
        form.cleaned_data["customer"] = self.request.user.username
        self.send_email(form)
        messages.success(self.request, "Se ha notificado correctamente que falta un producto. ¡Gracias!")
        return response

    def send_email(self, form):
        from_email = settings.DEFAULT_FROM_EMAIL
        to_emails = [self.request.user.email]
        subject = "Falta un producto - App Lupierra"
        context = {
            "form": form,
        }
        message = render_to_string("emails/missing_product.txt", context=context, request=self.request)

        send_mail(subject, message, from_email, to_emails, fail_silently=False)
        mail_managers(subject, message, fail_silently=False)


class CustomerDeliveryNoteCurrentMonthArchiveView(CustomerAuthMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        now = timezone.now()
        return reverse("lupanes:deliverynote-month-customer", args=(now.year, now.month))


class CustomerDeliveryNoteMonthArchiveView(CustomerAuthMixin, MonthArchiveView):
    template_name = "lupanes/my_deliverynote_archive_month.html"
    queryset = DeliveryNote.objects.all()
    date_field = "date"
    ordering = "date"
    allow_empty = True

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        return qs.filter(customer=self.request.user)
