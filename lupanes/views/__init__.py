from lupanes.views.customer import (
    CustomerDeliveryNoteCurrentMonthArchiveView,
    CustomerDeliveryNoteMonthArchiveView, DeliveryNoteCreateView,
    DeliveryNoteDeleteView, DeliveryNoteUpdateView, ProductAjaxView,
    ProductListView, ProductNewPriceView, ProductUpdateView)
from lupanes.views.manager import (CustomerListView,
                                   DeliveryNoteCurrentMonthArchiveView,
                                   DeliveryNoteMonthArchiveView,
                                   DeliveryNoteSummaryView)

__all__ = [
    "CustomerListView",
    "CustomerDeliveryNoteCurrentMonthArchiveView",
    "CustomerDeliveryNoteMonthArchiveView",
    "DeliveryNoteMonthArchiveView",
    "DeliveryNoteCreateView",
    "DeliveryNoteCurrentMonthArchiveView",
    "DeliveryNoteDeleteView",
    "DeliveryNoteUpdateView",
    "DeliveryNoteSummaryView",
    "ProductAjaxView",
    "ProductListView",
    "ProductNewPriceView",
    "ProductUpdateView",
]
