from django.urls import path
from .views import index, req, verfication

urlpatterns = [
    path("", index, name="index"),
    path("request/", req, name="req_page"),
    path("verify", verfication, name="verify")
]
