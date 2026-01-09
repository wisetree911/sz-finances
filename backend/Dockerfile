FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

WORKDIR /backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /backend/app
COPY ./alembic.ini /backend/alembic.ini
COPY ./entrypoint.sh /backend/entrypoint.sh
COPY ./migrations /backend/migrations
COPY ./shared /backend/shared

RUN chmod +x /backend/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/backend/entrypoint.sh"]
