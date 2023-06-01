FROM python:3.10 AS base

LABEL maintainer="Cihat Ertem"
LABEL website="https://cihatertem.dev"

COPY requirements.txt /tmp/requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential python3-dev libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install --upgrade --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt \
    && adduser \
    --quiet \
    --gecos "" \
    --disabled-password \
    --no-create-home \
    django-user \
    && mkdir -p /vol/web/media \
    && mkdir -p  /vol/web/static \
    && chown -R django-user:django-user /vol \
    && chmod -R 755 /vol

ENV PATH="/venv/bin:$PATH"

ENV PYTHONUNBUFFERED=1

ENV DEBUG_MODE=True

EXPOSE 8000

### Development Stage
FROM base AS dev

COPY requirements_dev.txt /tmp/requirements_dev.txt

RUN /venv/bin/pip install --upgrade --no-cache-dir -r /tmp/requirements_dev.txt \
    && rm /tmp/requirements_dev.txt

COPY /app /app

WORKDIR /app

RUN chown -R django-user:django-user /app

USER django-user

CMD python manage.py wait_for_db \
    && python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py runserver 0.0.0.0:8000

### Linting & Test Stage
FROM dev AS linting_testing

ENV DEBUG_MODE=False

CMD python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py test && flake8

### Production Section
FROM base as prod

COPY /scripts /scripts

COPY requirements_prod.txt /tmp/requirements_prod.txt

RUN /venv/bin/pip install --upgrade --no-cache-dir -r /tmp/requirements_prod.txt \
    && rm /tmp/requirements_prod.txt \
    && chmod -R +x /scripts

COPY /app /app

WORKDIR /app

RUN chown -R django-user:django-user /app

USER django-user

# uwsgi script port setup
EXPOSE 9000

ENV PATH="/scripts:/venv/bin:$PATH"

CMD [ "run.sh" ]