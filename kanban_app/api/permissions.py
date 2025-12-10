from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound
from kanban_app.models import Board, Task


class IsBoardOwnerOrMemberHelper:
    """Shared helper that checks if user belongs to a board."""

    @staticmethod
    def has_board_permission(board, account):
        return (
            board.owner_id == account.id or board.members.filter(id=account.id).exists()
        )


class IsBoardOwnerOrMember(BasePermission):
    """
    Permission for BoardViewSet.
    - On create: check membership based on `board` field in request.data
    - On object operations: check board owner/member
    """

    def has_permission(self, request, view):
        # ViewSet create action
        if getattr(view, "action", None) == "create":
            board_id = request.data.get("board")
            if not board_id:
                return False

            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                raise NotFound("Board does not exist")

            account = request.user.account
            return IsBoardOwnerOrMemberHelper.has_board_permission(board, account)

        return True

    def has_object_permission(self, request, view, board):
        account = request.user.account
        return IsBoardOwnerOrMemberHelper.has_board_permission(board, account)


class CanAccessTask(BasePermission):
    """User must be owner or member of the task's board."""

    def has_object_permission(self, request, view, task):
        account = request.user.account
        return IsBoardOwnerOrMemberHelper.has_board_permission(task.board, account)


class CanAccessTaskComments(BasePermission):
    """Permission for listing/creating/updating/deleting task comments."""

    def has_permission(self, request, view):
        # Generic views: ListCreateAPIView & RetrieveUpdateDestroyAPIView
        task_id = view.kwargs.get("task_id")
        if not task_id:
            return False

        try:
            task = Task.objects.select_related("board").get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task does not exist")

        account = request.user.account
        return IsBoardOwnerOrMemberHelper.has_board_permission(task.board, account)

    def has_object_permission(self, request, view, comment):
        # Comment object → check permission on its task's board
        task = comment.task
        return CanAccessTask().has_object_permission(request, view, task)


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, board):
        account = request.user.account
        return board.owner_id == account.id


class IsTaskOrBoardOwner(BasePermission):
    def has_object_permission(self, request, view, task):
        account = request.user.account
        return task.board.owner_id == account.id or task.created_by_id == account.id


class IsCommentOwner(BasePermission):
    def has_object_permission(self, request, view, comment):
        account = request.user.account
        return comment.author_id == account.id
