from lupanes.views.customer import (DeliveryNoteCreateView,
                                    DeliveryNoteDeleteView,
                                    DeliveryNoteUpdateView, ProductAjaxView,
                                    ProductListView, ProductNewPriceView,
                                    ProductUpdateView)
from lupanes.views.manager import (CustomerListView, DeliveryNoteListView,
                                   DeliveryNoteMonthArchiveView,
                                   DeliveryNoteSummaryView)

__all__ = [
    "CustomerListView",
    "DeliveryNoteMonthArchiveView",
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
