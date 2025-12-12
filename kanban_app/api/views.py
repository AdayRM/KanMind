"""Views for the Kanban application API endpoints."""

# Third party imports
from rest_framework import viewsets, mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

# Local imports
from auth_app.models import Account
from kanban_app.api.serializers import AccountSerializer, CommentSerializer
from kanban_app.api.permissions import (
    CanAccessTask,
    CanAccessTaskComments,
    IsBoardOwner,
    IsBoardOwnerOrMember,
    IsTaskOrBoardOwner,
    IsCommentOwner,
)
from kanban_app.api.serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    TaskSerializer,
)
from kanban_app.models import Board, Comment, Task

# Django imports
from django.db.models import Q
from django.shortcuts import get_object_or_404


""" 
Obj permissions will only apply to retrieve,update or delete. For lists we use get_queryset to filter the response
"""


class BoardViewSet(viewsets.ModelViewSet):
    """Manage boards the user owns or is a member of.

    - `list`: Returns boards where the requester is owner or member.
    - `create`: Allows authenticated users; ownership set in serializer.
    - `partial_update`: Update title/members via `BoardUpdateSerializer`.
    - `retrieve`: Returns full board details including members and tasks.
    - `destroy`: Restricted to board owner.
    """

    def get_permissions(self):
        """Return permissions based on action.

        - `create`: `IsAuthenticated`
        - `destroy`: `IsAuthenticated` and `IsBoardOwner`
        - others: `IsAuthenticated` and `IsBoardOwnerOrMember`
        """
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardOwnerOrMember()]

    def get_queryset(self):
        """Scope boards to those owned by or shared with the requester."""
        account = self.request.user.account
        return Board.objects.filter(Q(owner=account) | Q(members=account)).distinct()

    def get_serializer_class(self):
        """Select serializer by action for tailored payloads."""
        if self.action in ["list", "create"]:
            return BoardListSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return BoardDetailSerializer


class TasksAssignedListView(generics.ListAPIView):
    """List tasks where the requester is the `assignee`."""

    def get_queryset(self):
        """Return tasks assigned to the current account."""
        account = self.request.user.account
        return Task.objects.filter(assignee=account)

    serializer_class = TaskSerializer


class TasksReviewingListView(generics.ListAPIView):
    """List tasks where the requester is the `reviewer`."""

    def get_queryset(self):
        """Return tasks being reviewed by the current account."""
        account = self.request.user.account
        return Task.objects.filter(reviewer=account)

    serializer_class = TaskSerializer


class TasksCreateRetrieveUpdateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """CRUD operations for tasks with appropriate permissions.

    - `create`/`retrieve`/`update`: Requires authenticated user with
      access to the task's board (`CanAccessTask`).
    - `destroy`: Restricted to task creator or board owner
      (`IsTaskOrBoardOwner`).
    """

    queryset = Task.objects.all()

    def get_permissions(self):
        """Return permissions depending on action."""
        if self.action == "destroy":
            return [IsAuthenticated(), IsTaskOrBoardOwner()]

        return [IsAuthenticated(), CanAccessTask()]

    serializer_class = TaskSerializer


class EmailCheckView(APIView):
    """Resolve an account by email and return basic account data.

    GET parameter `email` is required; responds with serialized
    `Account` data or 404 if not found.
    """

    def get(self, request):
        email = request.query_params.get("email")

        if email is None:
            raise ValidationError({"email": "Email is a required param"})

        account = get_object_or_404(Account, user__email=email)

        return Response(AccountSerializer(account).data)


class TaskCommentListCreateView(generics.ListCreateAPIView):
    """List and create comments for a given task.

    Requires `task_id` in the URL. Creation sets `author` to the
    requesting user's account.
    """

    serializer_class = CommentSerializer

    permission_classes = [IsAuthenticated & CanAccessTaskComments]

    def get_queryset(self):
        """Return comments associated with the task specified by `task_id`."""
        return Comment.objects.filter(task_id=self.kwargs["task_id"])

    def perform_create(self, serializer):
        """Persist a new comment, binding it to the task and author."""
        return serializer.save(
            task_id=self.kwargs["task_id"], author=self.request.user.account
        )


class TaskCommentDestroyView(generics.DestroyAPIView):
    """Delete a comment; only the comment owner may perform this action."""

    permission_classes = [IsAuthenticated & IsCommentOwner]

    def get_queryset(self):
        """Return comments for the task specified by `task_id`."""
        return Comment.objects.filter(task_id=self.kwargs["task_id"])

    serializer_class = CommentSerializer
