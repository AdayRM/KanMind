"""
This is the main source for the routes. Redirection to e.g. app apis should happen here
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("kanban_app.api.urls")),
    path("api/auth/", include("auth_app.api.urls")),
    path("api-auth", include("rest_framework.urls")),
]
