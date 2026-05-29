from django.urls import path  # type: ignore[import]
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("doctor/signup/", views.doctor_signup_view, name="doctor_signup"),
    path("doctor/login/", views.doctor_login_view, name="doctor_login"),
    path("doctor/dashboard/", views.doctor_dashboard_view, name="doctor_dashboard"),
]
