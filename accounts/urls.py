from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.custom_login, name="custom_login"),
    path("logout/", views.custom_logout, name="custom_logout"),
    path("signup/", views.patient_signup, name="patient_signup"),
]