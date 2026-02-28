from django.conf import settings
from django.db import models

from apps.core.mixins import SlugMixin
from apps.core.models import TimeStampedSoftDeleteModel

from .enums import CollaboratorRole, ProjectStatus, TaskPriority, TaskStatus


class Project(TimeStampedSoftDeleteModel, SlugMixin):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_projects",
        db_index=True,
    )
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["owner", "status"]),
        ]

    def __str__(self):
        return self.name

    def get_slug_source(self) -> str:
        return self.name


class Task(TimeStampedSoftDeleteModel, SlugMixin):
    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)

    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
        db_index=True,
    )
    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
        db_index=True,
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    due_date = models.DateField(null=True, blank=True, db_index=True)
    position = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["position", "-created_at"]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["project", "assignee"]),
            models.Index(fields=["project", "due_date"]),
        ]

    def __str__(self):
        return f"{self.project_id}:{self.title}"

    def get_slug_source(self) -> str:
        return self.title


class Collaborator(TimeStampedSoftDeleteModel):
    project = models.ForeignKey(
        Project, related_name="collaborators", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="collaborations",
        on_delete=models.PROTECT,
    )
    role = models.CharField(
        max_length=20,
        choices=CollaboratorRole.choices,
        default=CollaboratorRole.VIEWER,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"], name="uniq_project_user_collaborator"
            )
        ]
        indexes = [
            models.Index(fields=["project", "role"]),
        ]

    def __str__(self):
        return f"{self.user_id} -> project={self.project_id} ({self.role})"
