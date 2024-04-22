from django.contrib import admin
from django.urls import include, path
from register import views as register_views
from payapp import views as payapp_views

urlpatterns = [
    path('', payapp_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('conversion/', include('conversion.urls')),
    path("register/", register_views.register_user, name="register"),
    path("login/", register_views.login_user, name="login"),
    path("logout/", register_views.logout_user, name="logout"),
    path("send-money/", payapp_views.send_money, name="send_money"),
    path("request-money/", payapp_views.request_money, name="request_money"),
    path('reject-payment-request/<int:payment_request_id>/', payapp_views.reject_payment_request, name='reject_payment_request'),
    path('approve-payment-request/<int:payment_request_id>/', payapp_views.approve_payment_request, name='approve_payment_request'),
]