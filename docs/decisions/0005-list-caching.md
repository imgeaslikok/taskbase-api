# ADR 0005: List Endpoint Caching

## Status

Accepted

## Context

List endpoints are frequently accessed.

## Decision

Use short-lived cache (30 seconds).

## Consequences

### Positive

* Improved performance
* Reduced database load

### Negative

* Small staleness window

## Alternatives

No caching

Rejected due to performance impact.
