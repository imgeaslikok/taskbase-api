# ADR 0002: JWT Authentication

## Status

Accepted

## Context

The API requires stateless authentication.

## Decision

Use JWT with refresh token rotation and blacklist.

## Consequences

### Positive

* Stateless access tokens
* Supports logout
* Production-ready security

### Negative

* Slightly more complex than session auth

## Alternatives

Session authentication

Rejected because:

* Requires server state
* Less suitable for APIs
