#!/usr/bin/env bash
# Backup diario de core-01 con restic. Uso: backup.sh [run|verify|restore <snapshot>]
# Variables en /etc/hipomaster/backup.env: RESTIC_REPOSITORY(_2), RESTIC_PASSWORD_FILE, HC_URL,
# y credenciales del destino externo (B2_* o AWS_*).
set -euo pipefail
source /etc/hipomaster/backup.env
COMPOSE_DIR=${COMPOSE_DIR:-/opt/hipomaster/deploy/vm}
STAGE=/var/backups/hipomaster
mkdir -p "$STAGE"

ping_hc() { curl -fsS -m 10 "${HC_URL}${1:-}" >/dev/null || true; }

run() {
  ping_hc /start
  docker compose -f "$COMPOSE_DIR/docker-compose.yml" exec -T postgres \
    pg_dumpall -U postgres | gzip > "$STAGE/pg_dumpall.sql.gz"
  # Documentos del cliente (volumen docs, ya cifrados por la app)
  DOCS=$(docker volume inspect -f '{{ .Mountpoint }}' vm_docs)
  for repo in "$RESTIC_REPOSITORY" "${RESTIC_REPOSITORY_2:-}"; do
    [ -z "$repo" ] && continue
    RESTIC_REPOSITORY=$repo restic backup "$STAGE" "$DOCS" "$COMPOSE_DIR/.env" --tag diario
    RESTIC_REPOSITORY=$repo restic forget --prune --keep-daily 7 --keep-weekly 4 --keep-monthly 6
  done
  rm -f "$STAGE/pg_dumpall.sql.gz"
  ping_hc
}

verify() {
  # Restaura el último dump en un Postgres temporal y comprueba que hay tablas.
  tmp=$(mktemp -d)
  restic restore latest --target "$tmp" --include "$STAGE/pg_dumpall.sql.gz"
  docker run -d --rm --name pg-verify -e POSTGRES_PASSWORD=verify pgvector/pgvector:pg16
  sleep 10
  gunzip -c "$tmp$STAGE/pg_dumpall.sql.gz" | docker exec -i pg-verify psql -U postgres -q
  docker exec pg-verify psql -U postgres -d hipomaster -tAc "select count(*) from pg_tables where schemaname not in ('pg_catalog','information_schema')"
  docker stop pg-verify; rm -rf "$tmp"
}

case "${1:-run}" in
  run) run ;;
  verify) verify ;;
  restore) restic restore "${2:?snapshot}" --target / ;;
  *) echo "uso: $0 [run|verify|restore <snapshot>]"; exit 2 ;;
esac
