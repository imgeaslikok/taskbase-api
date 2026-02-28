from __future__ import annotations

from apps.core.rbac import RBACRules

from .enums import CollaboratorRole

# Common read roles within a project
_READ = frozenset(
    {
        CollaboratorRole.MAINTAINER,
        CollaboratorRole.DEVELOPER,
        CollaboratorRole.VIEWER,
    }
)


PROJECT_RULES = RBACRules[str](
    read_roles=_READ,
    write_roles=frozenset({CollaboratorRole.MAINTAINER}),
    manage_roles=frozenset({CollaboratorRole.MAINTAINER}),
    delete_roles=frozenset(),  # owner-only via bypass
)

TASK_RULES = RBACRules[str](
    read_roles=_READ,
    write_roles=frozenset({CollaboratorRole.MAINTAINER, CollaboratorRole.DEVELOPER}),
    manage_roles=frozenset(),  # not used for tasks
    delete_roles=frozenset({CollaboratorRole.MAINTAINER, CollaboratorRole.DEVELOPER}),
)

COLLABORATOR_RULES = RBACRules[str](
    read_roles=_READ,
    write_roles=frozenset(),  # not used; collaborator mutations go through manage/delete
    manage_roles=frozenset({CollaboratorRole.MAINTAINER}),
    delete_roles=frozenset({CollaboratorRole.MAINTAINER}),
)
