from django.urls import path

from lupanes import views

app_name = "lupanes"

urlpatterns = [
    path('albaran/new/', views.DeliveryNoteCreateView.as_view(), name='deliverynote-new'),
]
