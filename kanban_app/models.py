"""Models for the Kanban application, including boards, tasks, and comments."""

# Django imports
from django.db import models
from auth_app.models import Account


class Board(models.Model):
    """A kanban board owned by an account and shared with members."""

    title = models.CharField(max_length=30)
    owner = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="boards_owned"
    )
    members = models.ManyToManyField(Account, related_name="boards_member_of")

    def __str__(self):
        """Return the board title for readable representation."""
        return self.title


class Task(models.Model):
    """A task item belonging to a board with workflow attributes."""

    class Status(models.TextChoices):
        TODO = "to-do", "To-do"
        IN_PROGRESS = "in-progress", "In Progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=80)
    description = models.CharField(max_length=225, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    priority = models.CharField(max_length=20, choices=Priority.choices)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    created_by = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assignee = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    reviewer = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_reviewer_of",
    )
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        """Return the task title for readable representation."""
        return self.title


class Comment(models.Model):
    """A comment authored by a user and attached to a task."""

    author = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        """Return the comment content for readable representation."""
        return self.content
