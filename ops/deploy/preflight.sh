#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/../.."

ENV_FILE=".env.docker"
PROJECT="grammar-mastery-advanced"
OLD_PROJECT="grammar-mastery"
OLD_FRONTEND_PORT="3005"
OLD_BACKEND_PORT="8005"
DEFAULT_FRONTEND_PORT="3006"
DEFAULT_BACKEND_PORT="8006"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

read_env_value() {
  local key="$1"
  local fallback="$2"
  local value
  value="$(awk -F= -v key="$key" '$1 == key {sub(/^[^=]*=/, ""); print; exit}' "$ENV_FILE" 2>/dev/null || true)"
  printf '%s' "${value:-$fallback}"
}

command -v docker >/dev/null 2>&1 || fail "docker is not installed."
docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 is not available."
command -v ss >/dev/null 2>&1 || fail "ss (iproute2) is required for the port check."
[[ -f "$ENV_FILE" ]] || fail "Missing $ENV_FILE. Copy docker.env.example to .env.docker and fill the secrets first."

FRONTEND_PORT="$(read_env_value FRONTEND_PORT "$DEFAULT_FRONTEND_PORT")"
BACKEND_PORT="$(read_env_value BACKEND_PORT "$DEFAULT_BACKEND_PORT")"
COMPOSE_NAME="$(read_env_value COMPOSE_PROJECT_NAME "$PROJECT")"

[[ "$COMPOSE_NAME" == "$PROJECT" ]] || fail "COMPOSE_PROJECT_NAME must be $PROJECT, got $COMPOSE_NAME."
[[ "$FRONTEND_PORT" != "$OLD_FRONTEND_PORT" ]] || fail "Frontend port collides with the existing site ($OLD_FRONTEND_PORT)."
[[ "$BACKEND_PORT" != "$OLD_BACKEND_PORT" ]] || fail "Backend port collides with the existing site ($OLD_BACKEND_PORT)."
[[ "$FRONTEND_PORT" != "$BACKEND_PORT" ]] || fail "Frontend and backend host ports must be different."

for port in "$FRONTEND_PORT" "$BACKEND_PORT"; do
  if ss -ltnH | awk '{print $4}' | grep -Eq "(^|:)$port$"; then
    fail "Host TCP port $port is already listening. Choose a free Advanced-only port before deploy."
  fi
done

# Rendering with --env-file catches missing required interpolation variables.
docker compose --env-file "$ENV_FILE" -p "$PROJECT" config --quiet

printf '\nAdvanced deployment preflight passed.\n'
printf '  Existing project: %s (known host ports %s/%s)\n' "$OLD_PROJECT" "$OLD_FRONTEND_PORT" "$OLD_BACKEND_PORT"
printf '  Advanced project: %s\n' "$PROJECT"
printf '  Advanced frontend: 127.0.0.1:%s -> container 3000\n' "$FRONTEND_PORT"
printf '  Advanced backend:  127.0.0.1:%s -> container 8000\n' "$BACKEND_PORT"
printf '  Advanced volume:   grammar-mastery-advanced-postgres-data\n'
printf '  Advanced network:  grammar-mastery-advanced-app\n\n'

printf 'Existing Grammar Mastery containers (read-only inspection):\n'
docker ps --filter "label=com.docker.compose.project=$OLD_PROJECT" --format '  {{.Names}}  {{.Ports}}' || true

printf '\nHost resource snapshot (informational only):\n'
free -h 2>/dev/null | sed 's/^/  /' || true
df -h / 2>/dev/null | sed 's/^/  /' || true

if command -v nginx >/dev/null 2>&1; then
  printf '\nCurrent Nginx syntax check:\n'
  nginx -t
fi

printf '\nNo containers, networks, volumes, Nginx files, or certificates were changed by this script.\n'
