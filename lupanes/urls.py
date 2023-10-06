from django.urls import path

from lupanes import views

app_name = "lupanes"

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('albaran/new/', views.DeliveryNoteCreateView.as_view(), name='deliverynote-new'),
    path('albaran/missing-product/', views.NotifyMissingProductView.as_view(), name='missing-product'),
    path('albaran/<int:pk>/edit/', views.DeliveryNoteUpdateView.as_view(), name='deliverynote-edit'),
    path('albaran/<int:pk>/delete/', views.DeliveryNoteDeleteView.as_view(), name='deliverynote-delete'),

    path('mis-albaranes/', views.CustomerDeliveryNoteCurrentMonthArchiveView.as_view(),
         name='deliverynote-current-month-customer'),
    path('mis-albaranes/<int:year>/<int:month>/', views.CustomerDeliveryNoteMonthArchiveView.as_view(month_format="%m"),
         name='deliverynote-month-customer'),

    path('albaranes/', views.DeliveryNoteCurrentMonthArchiveView.as_view(), name='deliverynote-current-month'),
    path('albaranes/<int:year>/<int:month>/', views.DeliveryNoteMonthArchiveView.as_view(month_format="%m"),
         name='deliverynote-month'),
    path('albaranes/<int:year>/<int:month>/summary/', views.DeliveryNoteSummaryView.as_view(month_format="%m"),
         name='deliverynote-summary'),
    path('albaranes/new-bulk/', views.DeliveryNoteBulkCreateView.as_view(), name='deliverynote-new-bulk'),
    path('albaranes/<int:pk>/edit-bulk/', views.DeliveryNoteBulkUpdateView.as_view(), name='deliverynote-edit-bulk'),
    path('albaranes/<int:pk>/delete-bulk/', views.DeliveryNoteBulkDeleteView.as_view(),
         name='deliverynote-delete-bulk'),

    path('neveras/', views.CustomerListView.as_view(), name='customer-list'),

    path('product/<int:pk>/', views.ProductAjaxView.as_view(), name='product-detail'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/new/', views.ProductCreateView.as_view(), name='product-new'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-edit'),
    path('products/<int:pk>/new-price/', views.ProductNewPriceView.as_view(), name='product-new-price'),
]
