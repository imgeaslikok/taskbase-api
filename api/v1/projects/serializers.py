from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.projects.models import Collaborator, Project, Task

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]


class ProjectSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = ["slug", "name"]


class TaskSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    assignee = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "slug",
            "title",
            "status",
            "priority",
            "assignee",
            "due_date",
            "position",
        ]


class CollaboratorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Collaborator
        fields = ["user", "role"]


# Project Serializers


class ProjectWriteSerializer(serializers.ModelSerializer):
    """
    Create/Update serializer.
    owner is set server-side (request.user).
    """

    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = ["slug", "name", "description", "status"]
        read_only_fields = ["slug"]


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Fast list payload:
    - no nested heavy relations
    - counts are annotated in queryset (recommended)
    """

    slug = serializers.CharField(read_only=True)

    tasks_count = serializers.IntegerField(read_only=True)
    collaborators_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = ["slug", "name", "status", "tasks_count", "collaborators_count"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Detail payload:
    - controlled embed: previews (first N) + counts
    - previews come from Prefetch(to_attr=...) in queryset for zero extra queries
    """

    slug = serializers.CharField(read_only=True)
    owner = UserSerializer(read_only=True)

    tasks_count = serializers.IntegerField(read_only=True)
    collaborators_count = serializers.IntegerField(read_only=True)

    tasks_preview = serializers.SerializerMethodField()
    collaborators_preview = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "slug",
            "name",
            "description",
            "status",
            "owner",
            "tasks_count",
            "collaborators_count",
            "tasks_preview",
            "collaborators_preview",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_tasks_preview(self, obj):
        # ViewSet queryset: Prefetch("tasks", queryset=..., to_attr="tasks_preview")
        items = getattr(obj, "tasks_preview", None)
        if items is None:
            return []
        return TaskSerializer(items, many=True).data

    def get_collaborators_preview(self, obj):
        # ViewSet queryset: Prefetch("collaborators", queryset=..., to_attr="collaborators_preview")
        items = getattr(obj, "collaborators_preview", None)
        if items is None:
            return []
        return CollaboratorSerializer(items, many=True).data


# Task Serializers


class TaskWriteSerializer(serializers.ModelSerializer):
    """
    Create/Update serializer.
    - project is resolved by URL and set in the view's perform_create() func
    """

    slug = serializers.CharField(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = Task
        fields = [
            "slug",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "due_date",
            "position",
        ]
        read_only_fields = ["slug"]


class TaskListSerializer(serializers.ModelSerializer):
    """
    Fast list payload.
    """

    slug = serializers.CharField(read_only=True)
    assignee = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "slug",
            "title",
            "status",
            "priority",
            "assignee",
            "due_date",
            "position",
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Detail payload including project and assigned user
    """

    slug = serializers.CharField(read_only=True)
    project = ProjectSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "slug",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "due_date",
            "position",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# Collaborator Serializers


class CollaboratorWriteSerializer(serializers.ModelSerializer):
    """
    Add/update collaborator
    """

    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Collaborator
        fields = ["user_id", "role"]
        validators = []


class CollaboratorListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Collaborator
        fields = ["user", "role", "created_at", "updated_at"]
        read_only_fields = fields
