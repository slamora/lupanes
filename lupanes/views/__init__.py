from lupanes.views.customer import (
    DeliveryNoteCreateView,
    DeliveryNoteDeleteView,
    DeliveryNoteUpdateView,
    ProductAjaxView,
    ProductListView,
    ProductUpdateView,
    ProductNewPriceView,
)
from lupanes.views.manager import DeliveryNoteListView, DeliveryNoteSummaryView, CustomerListView

__all__ = [
    "CustomerListView",
    "DeliveryNoteCreateView",
    "DeliveryNoteDeleteView",
    "DeliveryNoteUpdateView",
    "DeliveryNoteListView",
    "DeliveryNoteSummaryView",
    "ProductAjaxView",
    "ProductListView",
    "ProductNewPriceView",
    "ProductUpdateView",
]
