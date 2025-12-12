"""URL routing for KanMind API endpoints.

Registers viewsets and defines paths for board and task operations,
including task assignment/review filters and task comment list/create
and delete endpoints. Uses DRF's `DefaultRouter` for standard REST
routes on boards and tasks.
"""

# Third party imports
from rest_framework.routers import DefaultRouter

# Django imports
from django.urls import include, path

# Local imports
from kanban_app.api.views import (
    BoardViewSet,
    EmailCheckView,
    TaskCommentListCreateView,
    TasksAssignedListView,
    TasksCreateRetrieveUpdateDestroyViewSet,
    TasksReviewingListView,
    TaskCommentDestroyView,
)

router = DefaultRouter()
router.register(r"boards", BoardViewSet, basename="board")
router.register(r"tasks", TasksCreateRetrieveUpdateDestroyViewSet, basename="tasks")


urlpatterns = [
    path("email-check/", EmailCheckView.as_view(), name="email_check"),
    path(
        "tasks/assigned-to-me/", TasksAssignedListView.as_view(), name="tasks_assigned"
    ),
    path("tasks/reviewing/", TasksReviewingListView.as_view(), name="tasks_reviewing"),
    path(
        "tasks/<int:task_id>/comments/",
        TaskCommentListCreateView.as_view(),
        name="task_comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:pk>/",
        TaskCommentDestroyView.as_view(),
        name="task_comments-detail",
    ),
    path("", include("auth_app.api.urls")),
    path("", include(router.urls)),
]
