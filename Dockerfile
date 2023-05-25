FROM python:3.10 AS base

LABEL maintainer="Cihat Ertem"
LABEL website="https://cihatertem.dev"

COPY /app /app

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /tmp \
    && adduser \
    --disabled-password \
    --no-create-home \
    django-user

ENV PATH="/venv/bin:$PATH"

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

RUN chown -R django-user:django-user /app 

### Development Stage
FROM base AS dev

COPY requirements_dev.txt /tmp/requirements_dev.txt

RUN /venv/bin/pip install --no-cache-dir -r /tmp/requirements_dev.txt \
    && rm -rf /tmp

USER django-user

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

### Linting & Test Stage
FROM dev AS linting_testing

CMD python manage.py test && flake8
