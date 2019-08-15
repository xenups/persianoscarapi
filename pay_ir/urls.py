from django.urls import path
from .views import index, req, verfication, CustomCheckoutDone

urlpatterns = [
    path("", index, name="index"),
    path("request/", req, name="req_page"),
    path("verify", verfication, name="verify"),
    path('redirect/', CustomCheckoutDone.as_view(), name='redirect')

]
