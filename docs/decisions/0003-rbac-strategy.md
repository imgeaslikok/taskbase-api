# ADR 0003: RBAC Authorization

## Status

Accepted

## Context

Projects have multiple roles with different permissions.

## Decision

Implement a simple RBAC rules engine.

## Consequences

### Positive

* Explicit and readable
* Easy to extend

### Negative

* Requires manual rule definition

## Alternatives

django-guardian

Rejected to keep system minimal.
