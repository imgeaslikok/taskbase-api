from django.urls import path
from rest_framework.routers import DefaultRouter

from .viewsets import (
    CollaboratorViewSet,
    ProjectViewSet,
    TaskViewSet,
)

"""
Router handles flat Project endpoints:

GET     /projects/
POST    /projects/
GET     /projects/{slug}/
"""

router = DefaultRouter()
router.register(r"", ProjectViewSet, basename="projects")


"""
Explicit nested routes for project-scoped resources.

Why explicit:
- clearer URL contract
- no extra dependency
- easier to reason about permissions and lookups
"""

task_list = TaskViewSet.as_view({"get": "list", "post": "create"})
task_detail = TaskViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "put": "update", "delete": "destroy"}
)

collaborator_list = CollaboratorViewSet.as_view({"get": "list", "post": "create"})
collaborator_detail = CollaboratorViewSet.as_view(
    {"patch": "partial_update", "put": "update", "delete": "destroy"}
)


urlpatterns = [
    # Router URLs (projects)
    *router.urls,
    # Nested Task endpoints
    path("<slug:project_slug>/tasks/", task_list, name="project-task-list"),
    path(
        "<slug:project_slug>/tasks/<slug:task_slug>/",
        task_detail,
        name="project-task-detail",
    ),
    # Nested Collaborator endpoints
    path(
        "<slug:project_slug>/collaborators/",
        collaborator_list,
        name="project-collaborator-list",
    ),
    path(
        "<slug:project_slug>/collaborators/<int:user_id>/",
        collaborator_detail,
        name="project-collaborator-detail",
    ),
]
