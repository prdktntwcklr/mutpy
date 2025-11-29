# Usage:
#   docker build -t python-test .
#   docker run python-test

FROM python:3.6-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements/development.txt

CMD ["pytest", ".", "-vv"]
