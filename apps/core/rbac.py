from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Generic, Optional, TypeVar

RoleT = TypeVar("RoleT")


@dataclass(frozen=True)
class Scope(Generic[RoleT]):
    """
    Generic authorization scope.
    - role: scoped role for the current resource (or None if not a member)
    - bypass: grants full access (domain decides what "bypass" means; e.g. owner)
    """

    role: Optional[RoleT]
    bypass: bool


@dataclass(frozen=True)
class RBACRules(Generic[RoleT]):
    """
    Generic RBAC ruleset. Role semantics live in the configured sets.
    """

    read_roles: FrozenSet[RoleT]
    write_roles: FrozenSet[RoleT]
    manage_roles: FrozenSet[RoleT]
    delete_roles: FrozenSet[RoleT]

    def can_read(self, scope: Scope[RoleT]) -> bool:
        return bool(
            scope.bypass or (scope.role is not None and scope.role in self.read_roles)
        )

    def can_write(self, scope: Scope[RoleT]) -> bool:
        return bool(
            scope.bypass or (scope.role is not None and scope.role in self.write_roles)
        )

    def can_manage(self, scope: Scope[RoleT]) -> bool:
        return bool(
            scope.bypass or (scope.role is not None and scope.role in self.manage_roles)
        )

    def can_delete(self, scope: Scope[RoleT]) -> bool:
        return bool(
            scope.bypass or (scope.role is not None and scope.role in self.delete_roles)
        )
