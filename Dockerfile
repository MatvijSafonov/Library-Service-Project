# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base
LABEL maintainers="Team Undead Unicorns"

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Flag to indicate that the application is running inside a Docker container.
# This can be used to adjust application behavior when running in Docker.
ENV IN_DOCKER=1

WORKDIR /app

# Install system dependencies.
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files.
COPY pyproject.toml poetry.lock /app/

# Install project dependencies.
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copy the source code into the container.
COPY . /app/

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/bin/bash" \
    --no-create-home \
    --uid "${UID}" \
    django-user

RUN mkdir -p /app/celerybeat \
    && chmod +x /app/entrypoint.sh \
    && chown -R django-user:django-user /app

# Switch to the non-privileged user to run the application.
USER django-user

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
