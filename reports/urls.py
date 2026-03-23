from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_home, name='report_home'),
    path('stock/', views.stock_report, name='stock_report'),
    path('sales/', views.sales_report, name='sales_report'),
    path('purchases/', views.purchase_report, name='purchase_report'),
    path('expiry/', views.expiry_report, name='expiry_report'),

    path('stock/print/', views.print_stock_report, name='print_stock_report'),
    path('sales/print/', views.print_sales_report, name='print_sales_report'),
    path('purchases/print/', views.print_purchase_report, name='print_purchase_report'),
    path('expiry/print/', views.print_expiry_report, name='print_expiry_report'),
]