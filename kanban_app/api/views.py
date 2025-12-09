from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from kanban_app.api.serializers import AccountSerializer
from auth_app.models import Account
from kanban_app.api.permissions import (
    IsBoardOwner,
    IsBoardOwnerOrMember,
    IsTaskBoardOwnerOrMember,
    IsTaskOrBoardOwner,
)
from kanban_app.api.serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    TaskSerializer,
)
from kanban_app.models import Board, Task
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


class TasksAssignedListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    def get_queryset(self):
        account = self.request.user.account
        return Task.objects.filter(assignee=account)

    serializer_class = TaskSerializer


class TasksReviewingListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
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

        return [IsAuthenticated(), IsTaskBoardOwnerOrMember()]

    serializer_class = TaskSerializer


class EmailCheckView(APIView):
    def get(self, request):
        email = request.query_params.get("email")

        if email is None:
            raise ValidationError({"email": "Email is a required param"})

        account = get_object_or_404(Account, user__email=email)

        return Response(AccountSerializer(account).data)
