from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.plan_list, name='plan_list'),
    path('status/', views.subscription_status, name='subscription_status'),
    path('choose/<int:plan_id>/', views.choose_plan, name='choose_plan'),
    path('callback/', views.paystack_callback, name='paystack_callback'),
]