from django.urls import path
from conversion.views import ConvertCurrency

urlpatterns = [
    path('<str:base_currency>/<str:target_currency>/<str:amount>/', ConvertCurrency.as_view(), name='convert_currency'),
]
