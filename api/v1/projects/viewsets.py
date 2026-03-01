import logging

from django.db import transaction
from django.db.models import Count, Prefetch, Q
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.common.cache import cache_list_response
from api.common.enums import EventType
from api.common.events import log_event
from apps.projects.exceptions import InvalidTaskStatus, TaskConcurrencyError
from apps.projects.models import Collaborator, Project, Task
from apps.projects.use_cases import add_collaborator, transition_task_status

from .exceptions import ConcurrencyConflict
from .filters import CollaboratorFilter, ProjectFilter, TaskFilter
from .mixins import ProjectScopedMixin
from .permissions import CollaboratorPermission, TaskPermission
from .serializers import (
    CollaboratorListSerializer,
    CollaboratorWriteSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectWriteSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    TaskWriteSerializer,
)


class ProjectViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Project endpoints

    - list: fast overview with counts
    - retrieve: detailed view with limited previews
    - create: creates project owned by current user

    Notes:
    - Uses slug for lookup (stable public identifier)
    - Optimizes queries to avoid N+1 problems
    """

    permission_classes = [IsAuthenticated]

    lookup_field = "slug"

    filterset_class = ProjectFilter

    ordering_fields = ["created_at", "updated_at", "name", "status"]
    ordering = ["-created_at"]

    search_fields = ["name", "description"]

    serializer_classes = {
        "list": ProjectListSerializer,
        "retrieve": ProjectDetailSerializer,
        "create": ProjectWriteSerializer,
    }
    default_serializer_class = ProjectListSerializer

    def get_queryset(self):
        """
        Base queryset

        - Scopes projects to the current user (owner or collaborator)
        - Adds task/collaborator counts for list and detail views.
        - Adds limited previews only for detail view to keep list fast.
        """

        user = self.request.user

        qs = Project.objects.filter(
            Q(owner=user) | Q(collaborators__user=user)
        ).distinct()

        qs = qs.annotate(
            tasks_count=Count("tasks", distinct=True),
            collaborators_count=Count("collaborators", distinct=True),
        )

        if self.action == "retrieve":
            tasks_preview_qs = Task.objects.select_related("assignee").order_by(
                "position", "-created_at"
            )[:10]

            collaborators_preview_qs = Collaborator.objects.select_related(
                "user"
            ).order_by("-created_at")[:10]

            qs = qs.select_related("owner").prefetch_related(
                Prefetch("tasks", queryset=tasks_preview_qs, to_attr="tasks_preview"),
                Prefetch(
                    "collaborators",
                    queryset=collaborators_preview_qs,
                    to_attr="collaborators_preview",
                ),
            )

        return qs

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @cache_list_response(ttl=30, prefix="projects:list:v1")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        log_event(
            logging.INFO,
            EventType.PROJECT_CREATED,
            project=project.slug,
            owner_id=project.owner_id,
        )


class TaskViewSet(
    ProjectScopedMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Tasks under a project (nested resource).

    Endpoints:
    - GET    /projects/{project_slug}/tasks/
    - POST   /projects/{project_slug}/tasks/
    - GET    /projects/{project_slug}/tasks/{task_slug}/
    - PATCH  /projects/{project_slug}/tasks/{task_slug}/
    - DELETE /projects/{project_slug}/tasks/{task_slug}/
    """

    permission_classes = [TaskPermission]

    lookup_field = "slug"
    lookup_url_kwarg = "task_slug"

    filterset_class = TaskFilter
    ordering_fields = [
        "created_at",
        "updated_at",
        "title",
        "status",
        "priority",
        "due_date",
        "position",
    ]
    ordering = ["position", "-created_at"]
    search_fields = ["title", "description"]

    serializer_classes = {
        "list": TaskListSerializer,
        "retrieve": TaskDetailSerializer,
        "create": TaskWriteSerializer,
        "update": TaskWriteSerializer,
        "partial_update": TaskWriteSerializer,
    }
    default_serializer_class = TaskListSerializer

    def get_queryset(self):
        """
        Always scope tasks to the current project.
        Also selects related objects to avoid N+1.
        """
        project = self.get_project()
        return Task.objects.filter(project=project).select_related(
            "assignee", "project"
        )

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def perform_create(self, serializer):
        project = self.get_project()
        task = serializer.save(project=project)
        log_event(
            logging.INFO,
            EventType.TASK_CREATED,
            project=project.slug,
            task=task.slug,
            actor_id=self.request.user.id,
        )

    def perform_update(self, serializer):
        task = self.get_object()

        if "status" in serializer.validated_data:
            try:
                to_status = serializer.validated_data.pop("status")

                serializer.instance = transition_task_status(
                    task=task,
                    to_status=to_status,
                ).task
            except TaskConcurrencyError as exc:
                raise ConcurrencyConflict(str(exc)) from exc
            except InvalidTaskStatus as exc:
                raise ValidationError({"status": str(exc)}) from exc

        if serializer.validated_data:
            serializer.save()


class CollaboratorViewSet(
    ProjectScopedMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Collaborators under a project.

    Endpoints:
    - GET    /projects/{project_slug}/collaborators/
    - POST   /projects/{project_slug}/collaborators/            (add or restore)
    - PATCH  /projects/{project_slug}/collaborators/{user_id}/  (change role)
    - DELETE /projects/{project_slug}/collaborators/{user_id}/  (remove)

    Notes:
    - Lookup is by user_id (simple and stable)
    """

    permission_classes = [CollaboratorPermission]

    lookup_field = "user_id"
    lookup_url_kwarg = "user_id"

    filterset_class = CollaboratorFilter
    ordering_fields = ["created_at", "updated_at", "role"]
    ordering = ["-created_at"]
    search_fields = ["user__email"]

    serializer_classes = {
        "list": CollaboratorListSerializer,
        "create": CollaboratorWriteSerializer,
        "update": CollaboratorWriteSerializer,
        "partial_update": CollaboratorWriteSerializer,
    }
    default_serializer_class = CollaboratorListSerializer

    def get_queryset(self):
        """
        Always scope collaborators to the current project.
        select_related avoids N+1 for user fields.
        """
        project = self.get_project()
        return Collaborator.objects.filter(project=project).select_related(
            "user", "project"
        )

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def create(self, request, *args, **kwargs):
        """
        Add collaborator with restore semantics:
        - create if missing
        - restore if soft-deleted
        - update role if already active (idempotent)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        role = serializer.validated_data["role"]

        with transaction.atomic():
            result = add_collaborator(project=self.project, user=user, role=role)

            # Log one event; include flags for clarity
            log_event(
                logging.INFO,
                EventType.COLLABORATOR_ADDED,
                project=self.project.slug,
                actor_id=request.user.id,
                user_id=result.collaborator.user_id,
                role=result.collaborator.role,
                created=result.created,
                restored=result.restored,
                role_updated=result.role_updated,
            )

        # Response payload should reflect current state; list serializer is fine as output
        out = CollaboratorListSerializer(
            result.collaborator, context=self.get_serializer_context()
        )

        # Status code: 201 only when newly created; otherwise 200 (restore/update)
        return Response(
            out.data,
            status=status.HTTP_201_CREATED if result.created else status.HTTP_200_OK,
        )
