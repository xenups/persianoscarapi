from django.conf.urls import url
from django.urls import path

from checkout.views import PaymentFailed, CustomCheckoutDone
from .views import index, req, verification

urlpatterns = [
    path("", index, name="index"),
    path("request/", req, name="req_page"),
    path("verify", verification, name="verify"),
    path('redirect/', CustomCheckoutDone.as_view(), name='redirect'),
    path('payment-failed/', PaymentFailed.as_view(), name='payment-failed'),

]
