# ADR 0001: API Versioning Strategy

## Status

Accepted

## Context

The API must support future evolution without breaking existing clients.

## Decision

We use URL path versioning:

```
/api/v1/
```

## Consequences

### Positive

* Simple and explicit
* Easy for clients
* Easy to maintain

### Negative

* Requires URL duplication for new versions

## Alternatives Considered

Header-based versioning

Rejected because:

* Less explicit
* Harder to test manually
