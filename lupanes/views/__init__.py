from lupanes.views.customer import (
    CustomerDeliveryNoteCurrentMonthArchiveView,
    CustomerDeliveryNoteMonthArchiveView, DashboardView,
    DeliveryNoteCreateView, DeliveryNoteDeleteView, DeliveryNoteUpdateView,
    NotifyMissingProductView)
from lupanes.views.manager import (CustomerListView,
                                   DeliveryNoteBulkCreateView,
                                   DeliveryNoteCurrentMonthArchiveView,
                                   DeliveryNoteMonthArchiveView,
                                   DeliveryNoteSummaryView)
from lupanes.views.product import (ProductAjaxView, ProductCreateView,
                                   ProductListView, ProductNewPriceView,
                                   ProductUpdateView)

__all__ = [
    "DashboardView",
    "DeliveryNoteBulkCreateView",
    "CustomerDeliveryNoteCurrentMonthArchiveView",
    "CustomerDeliveryNoteMonthArchiveView",
    "CustomerListView",
    "DeliveryNoteMonthArchiveView",
    "DeliveryNoteCreateView",
    "DeliveryNoteCurrentMonthArchiveView",
    "DeliveryNoteDeleteView",
    "DeliveryNoteUpdateView",
    "DeliveryNoteSummaryView",
    "NotifyMissingProductView",
    "ProductAjaxView",
    "ProductCreateView",
    "ProductListView",
    "ProductNewPriceView",
    "ProductUpdateView",
]
