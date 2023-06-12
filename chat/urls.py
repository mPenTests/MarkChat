from django.urls import path
from . import views

urlpatterns = [
    path("api/register", views.register),
    path("api/verify/code", views.verify_verification_code),
    path("api/login", views.login),
    path("api/change/password", views.change_password),
    path("api/add/friend", views.add_friend)
]
