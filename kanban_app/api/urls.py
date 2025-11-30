from django.urls import path
from rest_framework.routers import DefaultRouter

from kanban_app.api.views import BoardViewSet

router = DefaultRouter()
router.register(r"boards", BoardViewSet, basename="board")
urlpatterns = router.urls
