from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('pharmacies/', views.pharmacy_list, name='admin_pharmacy_list'),
    path('pharmacies/<int:pk>/', views.pharmacy_detail, name='admin_pharmacy_detail'),
    path('pharmacies/<int:pk>/suspend/', views.suspend_pharmacy, name='suspend_pharmacy'),
    path('pharmacies/<int:pk>/activate/', views.activate_pharmacy, name='activate_pharmacy'),
    path('payments/', views.payment_list, name='admin_payment_list'),
    path('subscriptions/', views.subscription_list, name='admin_subscription_list'),
    path('plans/', views.plan_list_admin, name='admin_plan_list'),
]