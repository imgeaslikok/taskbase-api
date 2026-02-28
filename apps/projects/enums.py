from django.db import models


class ProjectStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    ARCHIVED = "archived", "Archived"


class TaskStatus(models.TextChoices):
    TODO = "todo", "To Do"
    IN_PROGRESS = "in_progress", "In Progress"
    IN_REVIEW = "in_review", "In Review"
    DONE = "done", "Done"


class TaskPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class CollaboratorRole(models.TextChoices):
    MAINTAINER = "maintainer", "Maintainer"
    DEVELOPER = "developer", "Developer"
    VIEWER = "viewer", "Viewer"
