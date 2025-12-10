from rest_framework import viewsets, mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from kanban_app.api.serializers import AccountSerializer, CommentSerializer
from auth_app.models import Account
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
from django.shortcuts import get_object_or_404


""" 
Obj permissions will only apply to retrieve,update or delete. For lists we use get_queryset to filter the response
"""


class BoardViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardOwnerOrMember()]

    def get_queryset(self):
        account = self.request.user.account
        return Board.objects.filter(Q(owner=account) | Q(members=account)).distinct()

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return BoardListSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return BoardDetailSerializer


class TasksAssignedListView(generics.ListAPIView):
    def get_queryset(self):
        account = self.request.user.account
        return Task.objects.filter(assignee=account)

    serializer_class = TaskSerializer


class TasksReviewingListView(generics.ListAPIView):
    def get_queryset(self):
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
    queryset = Task.objects.all()

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsTaskOrBoardOwner()]

        return [IsAuthenticated(), CanAccessTask()]

    serializer_class = TaskSerializer


class EmailCheckView(APIView):
    def get(self, request):
        email = request.query_params.get("email")

        if email is None:
            raise ValidationError({"email": "Email is a required param"})

        account = get_object_or_404(Account, user__email=email)

        return Response(AccountSerializer(account).data)


class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    permission_classes = [IsAuthenticated & CanAccessTaskComments]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"])

    def perform_create(self, serializer):
        return serializer.save(
            task_id=self.kwargs["task_id"], author=self.request.user.account
        )


class TaskCommentDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated & IsCommentOwner]

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"])

    serializer_class = CommentSerializer
