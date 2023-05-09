from django.views.generic.edit import CreateView

from lupanes.models import DeliveryNote


class DeliveryNoteCreateView(CreateView):
    model = DeliveryNote
    fields = ["customer", "product", "quantity"]
