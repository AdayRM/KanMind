""" "URL configuration for the auth_app API, including registration and login endpoints."""

# Django imports
from django.urls import path

# Local imports
from auth_app.api.views import LoginView, RegistrationView


urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]
