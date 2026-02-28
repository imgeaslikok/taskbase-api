FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Keep image small: only what we need for building wheels (e.g., psycopg)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install deps first for better layer caching
COPY requirements-base.txt requirements-prod.txt requirements-dev.txt /app/


# Prod deps
FROM base AS prod

RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "60"]


# Dev deps
FROM base AS dev

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]