from django.urls import path

from auth_app.api.views import AccountView, LoginView, RegistrationView


urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("accounts/", AccountView.as_view(), name="accounts"),
]
