from django.urls import path

from lupanes import views

app_name = "lupanes"

urlpatterns = [
    path('albaran/', views.DeliveryNoteListView.as_view(), name='deliverynote-list'),
    path('albaran/summary/', views.DeliveryNoteSummaryView.as_view(), name='deliverynote-summary'),
    path('albaran/new/', views.DeliveryNoteCreateView.as_view(), name='deliverynote-new'),
    path('albaran/<int:pk>/edit/', views.DeliveryNoteUpdateView.as_view(), name='deliverynote-edit'),
    path('albaran/<int:pk>/delete/', views.DeliveryNoteDeleteView.as_view(), name='deliverynote-delete'),

    path('neveras/', views.CustomerListView.as_view(), name='customer-list'),

    path('product/<int:pk>/', views.ProductAjaxView.as_view(), name='product-detail'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product-edit'),
    path('products/<int:pk>/new-price/', views.ProductNewPriceView.as_view(), name='product-new-price'),
]
