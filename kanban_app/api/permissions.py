from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound
from kanban_app.models import Board


class IsBoardOwnerOrMember(BasePermission):
    def has_permission(self, request, view):
        if view.action == "create":
            board_id = request.data.get("board")
            if not board_id:
                return False

            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                raise NotFound("Board does not exists")

            account = request.user.account
            return (
                board.owner == account or board.members.filter(id=account.id).exists()
            )

        return True

    def has_object_permission(self, request, view, obj):
        account = request.user.account
        return obj.owner == account or obj.members.filter(id=account.id).exists()


class IsTaskBoardOwnerOrMember(BasePermission):
    def has_permission(self, request, view):
        if view.action == "create":
            board_id = request.data.get("board")
            if not board_id:
                return False
            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                raise NotFound("Board does not exists")

            account = request.user.account
            return (
                board.owner == account or board.members.filter(id=account.id).exists()
            )

        return True

    def has_object_permission(self, request, view, obj):
        account = request.user.account
        return (
            obj.board.owner == account
            or obj.board.members.filter(id=account.id).exists()
        )


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        account = request.user.account
        return obj.owner == account


class IsTaskOrBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        account = request.user.account
        return obj.board.owner == account or obj.created_by == account
