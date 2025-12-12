from rest_framework import serializers

from auth_app.models import Account
from kanban_app.models import Board, Comment, Task


class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for listing boards with aggregate counts.

    Exposes counts for members, tickets, tasks in "todo" status,
    and high-priority tasks. Supports creation by assigning the
    requesting user's account as the board owner and setting members.
    """

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    def get_member_count(self, obj):
        """Return the number of members associated with the board."""
        return obj.members.count()

    def get_ticket_count(self, obj):
        """Return the number of tasks associated with the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Return the count of tasks on the board with status "todo"."""
        return obj.tasks.filter(status="todo").count()

    def get_tasks_high_prio_count(self, obj):
        """Return the count of tasks on the board with priority "high"."""
        return obj.tasks.filter(priority="high").count()

    def create(self, validated_data):
        """Create a board owned by the requesting user and set members."""
        owner = self.context["request"].user.account
        members = validated_data.pop("members", [])
        board = Board.objects.create(owner=owner, **validated_data)
        board.members.set(members)
        return board

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
            "members",
        ]

        extra_kwargs = {"members": {"write_only": True}}


class AccountSerializer(serializers.ModelSerializer):
    """Lightweight account serializer exposing id, email, and fullname."""

    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Account
        fields = ["id", "email", "fullname"]


class BoardTaskSerializer(serializers.ModelSerializer):
    """Serializer for tasks within a board context, with comment count."""

    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, obj):
        """Return the number of comments attached to the task."""
        return obj.comments.count()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "created_by",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """Detailed board serializer with member and task nested data."""

    members = AccountSerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating board title and members.

    Provides read-only nested `owner_data` and `members_data` for
    convenience while accepting `members` as write-only ids.
    """

    owner_data = AccountSerializer(source="owner", read_only=True)
    members_data = AccountSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "members", "owner_data", "members_data"]
        extra_kwargs = {"members": {"write_only": True}}


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating tasks with validations.

    - Adds `comments_count` as a computed field.
    - Accepts `assignee_id` and `reviewer_id` for write operations while
      exposing nested `assignee` and `reviewer` as read-only.
    - Validates that assignee and reviewer belong to the task's board.
    - Prevents changing the board of an existing task on update.
    """

    comments_count = serializers.SerializerMethodField()
    assignee_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )
    assignee = AccountSerializer(read_only=True)
    reviewer = AccountSerializer(read_only=True)

    def get_comments_count(self, obj):
        """Return the number of comments attached to the task."""
        return obj.comments.count()

    def validate(self, data):
        """Apply business rules for task updates and assignments.

        Ensures that:
        - The task's board cannot be changed during update operations.
        - `assignee_id` and `reviewer_id`, if provided, reference members
          of the associated board.
        """
        board = data.get("board") or self.instance.board
        assignee_id = data.get("assignee_id")
        reviewer_id = data.get("reviewer_id")

        request = self.context["request"]

        if request.method in ["PATCH", "PUT"]:
            instance = self.instance

            if board and instance.board_id != board.id:
                raise serializers.ValidationError(
                    {"board": "Changing the board id is not allowed"}
                )
        if assignee_id and not board.members.filter(id=assignee_id).exists():
            raise serializers.ValidationError("Assignee is not member of this board")

        if reviewer_id and not board.members.filter(id=reviewer_id).exists():
            raise serializers.ValidationError("Reviewer is not member of this board")

        return data

    def create(self, validated_data):
        """Create a task, setting `created_by` and optional assignee/reviewer."""
        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)

        assignee = Account.objects.get(pk=assignee_id) if assignee_id else None
        reviewer = Account.objects.get(pk=reviewer_id) if reviewer_id else None

        account = self.context["request"].user.account

        return Task.objects.create(
            **validated_data, assignee=assignee, reviewer=reviewer, created_by=account
        )

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
            "assignee_id",
            "reviewer_id",
        ]
        extra_kwargs = {
            "assignee": {"read_only": True},
            "reviewer": {"read_only": True},
        }


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments. `author` is read-only and set server-side."""

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "author": {"read_only": True},
        }
