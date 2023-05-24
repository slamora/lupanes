from lupanes.views.customer import (
    CustomerLoginView,
    CustomerLogoutView,
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
    "CustomerLoginView",
    "CustomerLogoutView",
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