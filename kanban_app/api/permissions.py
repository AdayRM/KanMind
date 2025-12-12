"""Permissions for Kanban application API views."""

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound

from kanban_app.models import Board, Task


class IsBoardOwnerOrMemberHelper:
    """Shared helper that checks if an account belongs to a board.

    Provides a single static method to determine whether an `account`
    is either the owner of the given `board` or listed among its
    members.
    """

    @staticmethod
    def has_board_permission(board, account):
        """Return True if account is board owner or member; else False."""
        return (
            board.owner_id == account.id or board.members.filter(id=account.id).exists()
        )


class IsBoardOwnerOrMember(BasePermission):
    """
    Permission for views operating on boards.

    - For create actions, checks membership based on the `board` id
      provided in `request.data`.
    - For object-level operations on a board instance, ensures the user
      is either the board owner or a member.
    """

    def has_permission(self, request, view):
        """Check list/create permissions for board-related actions.

        Allows creation only when a valid `board` id is provided and the
        requester is the owner or a member of that board. Other actions
        defer to object-level checks.
        """
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
        """Object-level check: requester must be board owner or member."""
        account = request.user.account
        return IsBoardOwnerOrMemberHelper.has_board_permission(board, account)


class CanAccessTask(BasePermission):
    """Require board ownership or membership for task access."""

    def has_object_permission(self, request, view, task):
        """Object-level check: requester must be owner/member of task.board."""
        account = request.user.account
        return IsBoardOwnerOrMemberHelper.has_board_permission(task.board, account)


class CanAccessTaskComments(BasePermission):
    """Permission for accessing comments related to a specific task.

    Ensures the requester is a board owner or member of the task's
    board for both list/create and retrieve/update/destroy comment
    views.
    """

    def has_permission(self, request, view):
        """View-level check for comment endpoints using `task_id` in URL."""
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
        """Object-level check: permission is derived from the comment's task."""
        # Comment object → check permission on its task's board
        task = comment.task
        return CanAccessTask().has_object_permission(request, view, task)


class IsBoardOwner(BasePermission):
    """Allow access only to the owner of a board instance."""

    def has_object_permission(self, request, view, board):
        account = request.user.account
        return board.owner_id == account.id


class IsTaskOrBoardOwner(BasePermission):
    """Allow access to either the task creator or the board owner."""

    def has_object_permission(self, request, view, task):
        account = request.user.account
        return task.board.owner_id == account.id or task.created_by_id == account.id


class IsCommentOwner(BasePermission):
    """Allow access only to the author of a comment instance."""

    def has_object_permission(self, request, view, comment):
        account = request.user.account
        return comment.author_id == account.id
