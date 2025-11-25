from django.db import models
from auth_app.models import Account


class Board(models.Model):
    title = models.CharField(max_length=30)
    owner = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="boards_owned"
    )
    members = models.ManyToManyField(Account, related_name="boards_member_of")

    def __str__(self):
        return self.title


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To-do"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=80)
    description = models.CharField(max_length=225, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.TODO
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.LOW
    )
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
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
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
