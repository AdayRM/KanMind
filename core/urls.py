"""
URL configuration for the core project.
Includes admin site and API routes for kanban_app and auth_app."""

# Django imports
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),  # Kanban app API endpoints
]
