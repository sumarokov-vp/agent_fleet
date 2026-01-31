#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==> Building images..."
podman-compose build

echo ""
echo "==> Stopping services..."
podman-compose down

echo ""
echo "==> Starting services..."
podman-compose up -d

echo ""
echo "==> Done. Services:"
podman-compose ps
