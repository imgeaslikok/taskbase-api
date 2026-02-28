# TaskBase API

Production-minded Django REST Framework backend demonstrating real-world architecture, authorization, and operational patterns.

This project is intentionally minimal in scope but designed with the same principles used in production systems.

It serves as:

* a reference implementation
* a portfolio project
* a companion to the **Production-Ready Django** engineering blog series

---

# Why This Project Exists

Most tutorials focus on features.

This project focuses on **engineering decisions**.

Specifically:

* how to structure a Django codebase for long-term maintainability
* how to implement authentication and authorization correctly
* how to design APIs with performance and scalability in mind
* how to prepare a backend for production environments

The domain is simple. The architecture is not accidental.

---

# Core Features

* Multi-user project management
* Task management within project scope
* Role-Based Access Control (RBAC)
* JWT authentication with rotation and blacklist
* Soft delete support
* User-scoped data isolation
* Optimized list/detail API patterns
* Request-scoped observability

---

# Architecture Overview

The project follows a **modular monolith** architecture with clear separation between:

```
apps/     → domain layer
api/      → HTTP adapter layer
config/   → infrastructure and configuration
```

The API layer adapts domain logic to HTTP.

Domain logic is not coupled to Django REST Framework.

This improves maintainability and testability.

This structure allows the domain layer to evolve independently from the API layer.

Full architecture documentation:

```
docs/architecture.md
```

---

# Engineering Highlights

## Domain-based structure

Organized by business capability, not technical layer:

```
apps/
  users/
  projects/
  tasks/
```

This scales better than controller/service/repository separation in Django.

---

## Explicit RBAC authorization

Authorization is implemented using a dedicated rules engine.

Permissions are:

* explicit
* predictable
* testable

Instead of implicit framework magic.

---

## Soft delete instead of hard delete

All records use:

```
deleted_at timestamp
```

instead of being permanently removed.

This matches real production safety practices.

---

## Optimized query patterns

List and detail endpoints use different query strategies:

* list → minimal payload
* detail → expanded representation

Includes:

* select_related
* prefetch_related
* annotated counts

---

## Consistent error contract

All errors include:

* stable structure
* request ID
* predictable format

This improves production debugging.

---

## Observability

Each request includes a request ID.

Structured logs include:

* request metadata
* timing
* event context

---

# Infrastructure

Fully containerized.

Development:

* SQLite
* auto-reload

Production:

* PostgreSQL
* Gunicorn

Configured via environment variables.

Production configuration is designed to run behind a reverse proxy such as Nginx.

---

# Tech Stack

* Python 3.12
* Django
* Django REST Framework
* PostgreSQL
* Docker
* Gunicorn
* Pytest
* Ruff

---

# Project Structure

```
.
├── apps/
├── api/
├── config/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── Makefile
└── README.md
```

---

# API Surface

Base URL:

http://localhost:8000/api/v1/

Example endpoints:

POST   /auth/login/
GET    /auth/me/

GET    /projects/
POST   /projects/

GET    /projects/{slug}/tasks/
POST   /projects/{slug}/tasks/

---

# Quickstart

Clone repository:

```
git clone https://github.com/yourusername/taskbase-api.git
cd taskbase-api
```

Setup environment:

```
cp .env.example .env
```

Start development environment:

```
make dev
```

API:

```
http://localhost:8000
```

Run migrations:

```
make migrate
```

Run tests:

```
make test
```

---

# Running Production Environment

```
make prod
```

---

# Testing

Run:

```
make test
```

Includes:

* API tests
* permission tests
* authentication tests

---

# Design Goals

This project demonstrates:

* production-ready Django architecture
* clean and maintainable structure
* explicit authorization design
* performance-aware query patterns
* operational readiness mindset

It intentionally avoids unnecessary abstraction.

---

# Blog Series

This project accompanies the **Production-Ready Django** series.

The series explains:

* architecture decisions
* authentication implementation
* RBAC design
* Docker and deployment
* production readiness

https://medium.com/production-ready-django

---

# Status

This project is actively maintained and used as a reference implementation for production-ready Django architecture.

---

# License

MIT License
