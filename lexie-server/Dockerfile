# Lexie server — production-style image (WX-006 / M1).
# Build from this directory: docker build -t lexie-server .
FROM python:3.11-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY lexie_server ./lexie_server

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1
# Platforms often inject PORT; default matches local README.
ENV PORT=8000
# SQLite and profile DB live here — mount a volume at /data on ephemeral hosts.
ENV LEXIE_DATA_DIR=/data

RUN mkdir -p /data

EXPOSE 8000

CMD sh -c 'exec uvicorn lexie_server.main:app --host 0.0.0.0 --port "${PORT}"'
