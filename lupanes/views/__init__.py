from lupanes.views.customer import (
    CustomerDeliveryNoteCurrentMonthArchiveView,
    CustomerDeliveryNoteMonthArchiveView, DashboardView,
    DeliveryNoteCreateView, DeliveryNoteDeleteView, DeliveryNoteUpdateView,
    NotifyMissingProductView)
from lupanes.views.manager import (CustomerListView,
                                   DeliveryNoteBulkCreateView,
                                   DeliveryNoteBulkUpdateView,
                                   DeliveryNoteBulkDeleteView,
                                   DeliveryNoteCurrentMonthArchiveView,
                                   DeliveryNoteMonthArchiveView,
                                   DeliveryNoteSummaryView,
                                   ProductSummaryView)
from lupanes.views.product import (ProductAjaxView, ProductCreateView,
                                   ProductListView, ProductNewPriceView,
                                   ProductUpdateView)

__all__ = [
    "DashboardView",
    "DeliveryNoteBulkCreateView",
    "DeliveryNoteBulkUpdateView",
    "DeliveryNoteBulkDeleteView",
    "CustomerDeliveryNoteCurrentMonthArchiveView",
    "CustomerDeliveryNoteMonthArchiveView",
    "CustomerListView",
    "DeliveryNoteMonthArchiveView",
    "DeliveryNoteCreateView",
    "DeliveryNoteCurrentMonthArchiveView",
    "DeliveryNoteDeleteView",
    "DeliveryNoteUpdateView",
    "DeliveryNoteSummaryView",
    "ProductSummaryView",
    "NotifyMissingProductView",
    "ProductAjaxView",
    "ProductCreateView",
    "ProductListView",
    "ProductNewPriceView",
    "ProductUpdateView",
]
