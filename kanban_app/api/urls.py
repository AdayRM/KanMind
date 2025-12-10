from django.urls import include, path
from rest_framework.routers import DefaultRouter

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
    path("", include(router.urls)),
]
