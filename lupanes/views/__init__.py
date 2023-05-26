from lupanes.views.customer import (
    DeliveryNoteCreateView,
    DeliveryNoteDeleteView,
    DeliveryNoteUpdateView,
    ProductAjaxView,
    ProductListView,
    ProductUpdateView,
    ProductNewPriceView,
)
from lupanes.views.manager import DeliveryNoteListView, DeliveryNoteSummaryView

__all__ = [
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
