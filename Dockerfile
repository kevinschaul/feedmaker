ARG PYTHON_VERSION=3.10-slim-buster

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN mkdir -p /code

WORKDIR /code

# Copy dependency files
COPY pyproject.toml /code/
COPY uv.lock /code/

# Install dependencies using uv (skip installing the project itself for now)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application
COPY . /code/

# Now install the project itself
RUN uv sync --frozen --no-dev

#RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--access-logfile", "-", "--preload", "feedmaker.wsgi"]
