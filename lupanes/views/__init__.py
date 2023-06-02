from lupanes.views.customer import (
    CustomerDeliveryNoteCurrentMonthArchiveView,
    CustomerDeliveryNoteMonthArchiveView, DeliveryNoteCreateView,
    DeliveryNoteDeleteView, DeliveryNoteUpdateView, NotifyMissingProductView)
from lupanes.views.manager import (CustomerListView,
                                   DeliveryNoteCurrentMonthArchiveView,
                                   DeliveryNoteMonthArchiveView,
                                   DeliveryNoteSummaryView)
from lupanes.views.product import (ProductAjaxView, ProductListView,
                                   ProductNewPriceView, ProductUpdateView)

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
    "NotifyMissingProductView",
    "ProductAjaxView",
    "ProductListView",
    "ProductNewPriceView",
    "ProductUpdateView",
]
