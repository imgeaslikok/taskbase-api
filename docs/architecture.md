# TaskBase Architecture

## Overview

TaskBase is a minimal project and task management API built with Django REST Framework.
The goal is not feature richness, but to demonstrate production-ready architectural thinking with minimal complexity.

The architecture follows a **layered modular monolith** approach with clear separation between:

* Domain layer (`apps/`)
* API adapter layer (`api/`)
* Infrastructure and configuration (`config/`)

---

## Design Principles

### 1. Framework as Adapter, Not Core

The domain logic lives in `apps/`.
The `api/` layer adapts domain models and rules to HTTP.

This ensures the domain is not tightly coupled to Django REST Framework.

**Why**

* Improves testability
* Makes rules reusable outside HTTP
* Prevents framework lock-in

---

### 2. Stable Public Identifiers

All public resources use slugs instead of database IDs.

**Why**

* Prevents ID enumeration
* Provides stable external references
* Decouples API from database internals

Alternative considered: UUID
Slug was chosen for readability and demo clarity.

---

### 3. Explicit Authorization via RBAC Rules

Authorization is implemented using a simple Role-Based Access Control rules engine.

Rules are defined in the domain layer and enforced in the API layer.

**Why**

* Keeps permission logic explicit
* Avoids hidden magic
* Makes behavior easy to reason about

Alternative considered: django-guardian
Rejected to avoid unnecessary abstraction for this scope.

---

### 4. Soft Delete Instead of Hard Delete

Records are marked with `deleted_at` instead of being physically removed.

**Why**

* Prevents accidental data loss
* Allows recovery
* Matches real production practices

Alternative considered: hard delete
Rejected due to operational risk.

---

### 5. Optimized List vs Detail Queries

List endpoints return minimal data.
Detail endpoints return expanded representations.

**Why**

* Prevents unnecessary database load
* Improves API performance
* Matches real production API patterns

---

### 6. Consistent Error Contract

All errors follow a standard format and include a request ID.

**Why**

* Improves client handling
* Enables production debugging

---

### 7. Request-Scoped Observability

Each request has a request ID propagated through logs and responses.

**Why**

* Enables tracing
* Simplifies debugging

---

### 8. Environment Separation

Development uses SQLite.
Production uses PostgreSQL and Gunicorn.

**Why**

* Fast local setup
* Production parity where it matters

---

## Non-Goals

This project intentionally avoids:

* Microservices
* Repository pattern abstraction
* Over-engineering

The goal is clarity, not abstraction depth.

---

## Summary

TaskBase demonstrates how to structure a Django project with production-ready thinking while remaining minimal and understandable.
