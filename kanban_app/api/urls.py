from django.urls import include, path
from rest_framework.routers import DefaultRouter

from kanban_app.api.views import (
    BoardViewSet,
    EmailCheckView,
    TasksAssignedListViewSet,
    TasksCreateRetrieveUpdateDestroyViewSet,
    TasksReviewingListViewSet,
)

router = DefaultRouter()
router.register(r"boards", BoardViewSet, basename="board")
router.register(r"tasks", TasksCreateRetrieveUpdateDestroyViewSet, basename="tasks")
router.register(
    r"tasks/assigned-to-me", TasksAssignedListViewSet, basename="tasks_assigned"
)
router.register(
    r"tasks/reviewing", TasksReviewingListViewSet, basename="tasks_reviewing"
)

urlpatterns = [
    path("", include(router.urls)),
    path("email-check/", EmailCheckView.as_view(), name="email_check"),
]
