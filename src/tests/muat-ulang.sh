#!/usr/bin/env bash
# Memuat ulang konfigurasi (app1, app2, nginx) lalu memeriksa nginx.conf.
set -u
# Naik ke akar repository (src/tests -> akar) supaya path volume benar.
cd "$(dirname "$0")/../.." || exit 1

echo "=== terapkan ulang konfigurasi ==="
docker compose up -d --force-recreate app1 app2 nginx

echo
echo "=== tunggu semua container sehat ==="
for c in app1 app2 redis; do
  for _ in $(seq 1 25); do
    s=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}-{{end}}' \
        "mkkl1030-loadbalancer-redis-${c}-1" 2>/dev/null)
    [ "$s" = "healthy" ] && { echo "  $c: healthy"; break; }
    sleep 2
  done
done

echo
echo "=== uji nginx.conf di dalam container nginx yang berjalan ==="
docker compose exec -T nginx nginx -t 2>&1

echo
echo "=== status container ==="
docker compose ps
