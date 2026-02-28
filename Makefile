.PHONY: help dev prod down restart logs shell test lint format migrate createsuperuser


COMPOSE := docker compose

DEV_COMPOSE_FILES := -f docker-compose.dev.yml
PROD_COMPOSE_FILES := -f docker-compose.yml

DEV := $(COMPOSE) $(DEV_COMPOSE_FILES)
PROD := $(COMPOSE) $(PROD_COMPOSE_FILES)

API := api

help:
	@echo "Development (SQLite):"
	@echo "  make dev"
	@echo "  make down"
	@echo "  make restart"
	@echo "  make logs"
	@echo "  make shell"
	@echo "  make migrate"
	@echo "  make createsuperuser"
	@echo "  make test"
	@echo "  make lint"
	@echo "  make format"
	@echo ""
	@echo "Production:"
	@echo "  make prod"
	@echo ""

dev:
	$(DEV) up --build

down:
	$(DEV) down --remove-orphans

restart:
	$(DEV) down --remove-orphans
	$(DEV) up --build

logs:
	$(DEV) logs -f

shell:
	$(DEV) exec $(API) bash

migrate:
	$(DEV) exec $(API) python manage.py migrate

createsuperuser:
	$(DEV) exec $(API) python manage.py createsuperuser

test:
	$(DEV) exec -e DJANGO_ENV=test $(API) pytest

lint:
	$(DEV) exec $(API) ruff check .

format:
	$(DEV) exec $(API) ruff format .

prod:
	$(PROD) up --build -d