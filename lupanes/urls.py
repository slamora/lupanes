from django.urls import path

from lupanes import views

app_name = "lupanes"

urlpatterns = [
    path('auth/login/', views.CustomerLoginView.as_view(), name='customer-login'),
    path('auth/logout/', views.CustomerLogoutView.as_view(), name='customer-logout'),
    path('albaran/', views.DeliveryNoteListView.as_view(), name='deliverynote-list'),
    path('albaran/summary/', views.DeliveryNoteSummaryView.as_view(), name='deliverynote-summary'),
    path('albaran/new/', views.DeliveryNoteCreateView.as_view(), name='deliverynote-new'),
    path('albaran/<int:pk>/edit/', views.DeliveryNoteUpdateView.as_view(), name='deliverynote-edit'),
    path('albaran/<int:pk>/delete/', views.DeliveryNoteDeleteView.as_view(), name='deliverynote-delete'),
    path('product/<int:pk>/', views.ProductAjaxView.as_view(), name='product-detail'),
]
