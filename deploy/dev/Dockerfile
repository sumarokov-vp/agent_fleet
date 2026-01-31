FROM --platform=linux/arm64 python:3.14-slim

WORKDIR /app

# Установка системных зависимостей и Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
RUN pip install uv

# Entrypoint
ENTRYPOINT ["uv", "run"]
