from django.urls import path
from . import views

urlpatterns = [
    path("api/register", views.register),
    path("api/verify/code", views.verify_verification_code)
]
