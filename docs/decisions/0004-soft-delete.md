# ADR 0004: Soft Delete

## Status

Accepted

## Context

Deleted data may need recovery.

## Decision

Use soft delete via deleted_at timestamp.

## Consequences

### Positive

* Safe deletion
* Recoverable data

### Negative

* Slightly more query complexity

## Alternatives

Hard delete

Rejected due to data loss risk.
