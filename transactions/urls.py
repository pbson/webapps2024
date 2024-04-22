from django.urls import path
from . import views

urlpatterns = [
    path('', views.points_transfer, name='points_transfer'),
]
