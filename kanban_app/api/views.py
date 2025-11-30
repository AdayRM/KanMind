from rest_framework import viewsets
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from kanban_app.api.permissions import IsBoardOwner, IsBoardOwnerOrMember
from kanban_app.api.serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
)
from kanban_app.models import Board


""" 
Obj permissions will only apply to retrieve,update or delete. For lists we use get_queryset to filter the response
"""


class BoardViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == "destroy":
            return [IsBoardOwner()]
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
