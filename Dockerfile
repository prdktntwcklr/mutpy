ARG PYTHON_VERSION=3.9

FROM python:${PYTHON_VERSION}-slim

RUN apt-get update && apt-get install -y \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/app

COPY requirements/ ./requirements/

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements/development.txt
