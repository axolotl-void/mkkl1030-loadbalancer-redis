#!/usr/bin/env bash
# Skenario uji kegagalan untuk sistem load balancer + replicated app.
set -u

echo "=== 1. Keadaan normal: 10 permintaan, catat app yang melayani ==="
for i in $(seq 1 10); do curl -s http://localhost/ ; echo; done

echo
echo "=== 2. Beban tinggi: 1000 permintaan, 50 bersamaan ==="
if command -v hey >/dev/null; then
  hey -n 1000 -c 50 http://localhost/ | tail -20
else
  echo "hey tidak terpasang — lewati (pasang: brew install hey)"
fi

echo
echo "=== 3. Matikan app1 saat sistem berjalan ==="
docker compose stop app1
echo "--- permintaan setelah app1 mati (harus dijawab app2) ---"
for i in $(seq 1 5); do curl -s http://localhost/ ; echo; done
docker compose start app1

echo
echo "=== 4. Restart Redis dan periksa ketahanan status ==="
BEFORE=$(curl -s http://localhost/state)
docker compose restart redis
sleep 3
AFTER=$(curl -s http://localhost/state)
echo "sebelum: $BEFORE"
echo "sesudah: $AFTER"
