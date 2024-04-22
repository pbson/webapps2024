from django.urls import path
from . import views

urlpatterns = [
    path('', views.commentstore, name='commentstore'),
    path('home/', views.home, name="home"),
]
