from django.urls import path
from . import views

urlpatterns = [
    path('', views.drug_list, name='drug_list'),
    path('add/', views.add_drug, name='add_drug'),
    path('edit/<int:pk>/', views.edit_drug, name='edit_drug'),
    path('expiry-alerts/', views.expiry_alerts, name='expiry_alerts'),
    path('low-stock/', views.low_stock, name='low_stock'),
]