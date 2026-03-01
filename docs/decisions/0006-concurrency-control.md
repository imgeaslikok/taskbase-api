# ADR 0006: Concurrency Control Using PostgreSQL Advisory Locks

## Status

Accepted

## Context

Task status transitions may be triggered by multiple concurrent requests.

Without concurrency control, this can cause:

* race conditions
* lost updates
* inconsistent task state

Example:

Two users marking the same task as DONE at the same time.

The system must ensure task state transitions are safe and deterministic.

---

## Decision

Use PostgreSQL advisory locks to serialize task status transitions.

Each transition acquires a per-task advisory lock.

Example lock key pattern:

```
taskbase:task:{task_id}:transition:status
```

Locks are implemented using the django-concurrency-safe library.

---

## Consequences

### Positive

* Prevents race conditions
* Prevents lost updates
* Ensures consistent task state
* Explicit and predictable concurrency control
* Works reliably in distributed environments

### Negative

* PostgreSQL-specific implementation
* Adds small overhead to status transitions
* Requires PostgreSQL in all environments

---

## Alternatives Considered

### No explicit concurrency control

Rejected because:

* Allows race conditions
* Unsafe in production environments

---

### Database row locking (SELECT FOR UPDATE)

Rejected because:

* Coupled to transaction scope
* Harder to encapsulate cleanly in domain logic
* Less explicit as a concurrency mechanism

---

### Optimistic locking (version field)

Rejected because:

* Requires retry handling
* More complex client logic
* Less deterministic behavior

---

## Rationale

PostgreSQL advisory locks provide explicit, reliable, and production-proven concurrency control while keeping domain logic clear and maintainable.
