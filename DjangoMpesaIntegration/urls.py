from django.urls import path

from . import views

urlpatterns = [
    path('checkout/', views.MpesaCheckout.as_view()),
    path('callback/', views.MpesaCallBack.as_view())
]
