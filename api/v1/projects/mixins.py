from __future__ import annotations

from django.shortcuts import get_object_or_404

from apps.projects.models import Collaborator, Project


class ProjectScopedMixin:
    """
    Resolves the project from the URL and caches project scope on the request.

    Sets:
      - request.project
      - request.project_role
      - request.is_project_owner

    This mixin does not enforce permissions.
    Permission enforcement belongs to DRF permission classes.
    """

    project_lookup_kwarg = "project_slug"
    project = None  # cached project instance

    def get_project(self) -> Project:
        """Fetch and cache the project once per request."""
        if self.project is not None:
            return self.project

        slug = self.kwargs.get(self.project_lookup_kwarg)

        project = get_object_or_404(
            Project.objects.select_related("owner"),
            slug=slug,
        )

        self.project = project
        return project

    def init_project_scope(self) -> None:
        """
        Initialize and cache project scope on the request.
        Safe to call multiple times per request.
        """
        request = self.request

        if getattr(request, "_project_scope_ready", False):
            return

        project = self.get_project()
        request.project = project

        is_owner = bool(
            request.user
            and request.user.is_authenticated
            and project.owner_id == request.user.id
        )
        request.is_project_owner = is_owner

        role = None
        if request.user and request.user.is_authenticated and not is_owner:
            role = (
                Collaborator.objects.filter(project=project, user=request.user)
                .values_list("role", flat=True)
                .first()
            )

        request.project_role = role
        request._project_scope_ready = True

    def initial(self, request, *args, **kwargs):
        """
        DRF calls this before permissions.
        We must prepare scope after authentication but before permission checks.
        """
        # This mirrors rest_framework.views.APIView.initial, with one extra step:
        # init_project_scope() inserted between authentication and permission checks.

        self.format_kwarg = self.get_format_suffix(**kwargs)

        neg = self.perform_content_negotiation(request)
        request.accepted_renderer, request.accepted_media_type = neg

        request.version, request.versioning_scheme = self.determine_version(
            request, *args, **kwargs
        )

        self.perform_authentication(request)

        # Scope must be ready before DRF permission classes run
        self.init_project_scope()

        self.check_permissions(request)
        self.check_throttles(request)
