from django.contrib import admin

from kanban_app.models import Board, Comment, Task


class BoardAdmin(admin.ModelAdmin):
    fields = ["id", "title"]


# Register your models here.
admin.site.register(Board)
admin.site.register(Task)
admin.site.register(Comment)
