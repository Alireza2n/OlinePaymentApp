from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('prepare/', views.prepare_payment_view, name='prepare'),
    path('callback/', views.payment_callback_view, name='callback'),
]
