FROM --platform=linux/arm64 python:3.14-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install uv

# Entrypoint
ENTRYPOINT ["uv", "run"]
