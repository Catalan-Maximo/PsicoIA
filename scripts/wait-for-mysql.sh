#!/usr/bin/env bash
set -e
host="${1:-mysql}"
shift || true
until mysqladmin ping -h "$host" --silent; do
  echo "Esperando MySQL en $host..."
  sleep 2
done
echo "MySQL OK."
exec "$@"
