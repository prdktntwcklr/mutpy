# Usage:
#   docker build --build-arg PYTHON_VERSION=3.8 -t python-test .
#   docker run --rm python-test

ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY requirements/ ./requirements/

RUN pip install --no-cache-dir -r requirements/development.txt
