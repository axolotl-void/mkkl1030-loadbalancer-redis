#!/usr/bin/env python3
"""App server tanpa status sendiri.

Seluruh status disimpan di Redis supaya kedua salinan app server selalu
melihat data yang sama, dan supaya app server dapat dimatikan tanpa
kehilangan data.

Titik akhir:
  GET /        -> identitas app server + jumlah permintaan
  GET /health  -> status kesehatan (untuk pemeriksaan Nginx)
  GET /state   -> isi status bersama dari Redis
  GET /slow    -> simulasi permintaan lambat (untuk uji peralihan)

Variabel lingkungan:
  SERVER_NAME  nama app server (app1 / app2)
  REDIS_HOST   host Redis (default: localhost)
  REDIS_PORT   port Redis (default: 6379)
  PORT         port HTTP app server (default: 5001)
"""
from __future__ import annotations

import os
import time

from flask import Flask, jsonify
import redis

app = Flask(__name__)

SERVER_NAME = os.environ.get("SERVER_NAME", "app?")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

# decode_responses=True -> Redis mengembalikan str, bukan bytes.
# socket_connect_timeout dipasang pendek supaya permintaan tidak menggantung
# lama ketika Redis mati; penanganan kegagalannya ada di _redis_or_none().
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=1.0,
    socket_timeout=1.0,
)


def _redis_error_message(exc: Exception) -> str:
    """Pesan singkat dan seragam untuk kegagalan Redis."""
    return f"Redis tidak dapat dihubungi ({type(exc).__name__})"


@app.get("/")
def index():
    """Hitungan permintaan disimpan di Redis, bukan di memori proses.

    Karena itu app1 dan app2 menghitung ke total yang sama: mematikan salah
    satu app server tidak membuat angkanya kembali dari nol.
    """
    try:
        total = r.incr("permintaan_total")
        return jsonify({
            "server": SERVER_NAME,
            "permintaan_ke": total,
            "redis": "ok",
        })
    except redis.RedisError as exc:
        # Redis mati bukan alasan untuk menolak melayani permintaan:
        # app server tetap menjawab, tetapi menandai bahwa hitungan gagal.
        return jsonify({
            "server": SERVER_NAME,
            "permintaan_ke": None,
            "redis": "gagal",
            "pesan": _redis_error_message(exc),
        }), 200


@app.get("/health")
def health():
    """Pemeriksaan kesehatan untuk Nginx.

    Redis dianggap wajib: app server tanpa penyimpanan bersama tidak dapat
    memenuhi fungsinya, jadi statusnya 503 agar Nginx dapat membuang node ini
    dari perputaran permintaan.
    """
    try:
        r.ping()
        return jsonify({"status": "ok", "server": SERVER_NAME}), 200
    except redis.RedisError as exc:
        return jsonify({
            "status": "degraded",
            "server": SERVER_NAME,
            "pesan": _redis_error_message(exc),
        }), 503


@app.get("/state")
def state():
    """Isi status bersama. Dibaca ulang setelah Redis dimulai ulang untuk
    memperlihatkan bahwa data bertahan (appendonly yes pada docker-compose).
    """
    try:
        total = r.get("permintaan_total")
        kunci = sorted(r.keys("*"))
        return jsonify({
            "server": SERVER_NAME,
            "permintaan_total": total,
            "kunci": kunci,
        }), 200
    except redis.RedisError as exc:
        return jsonify({
            "server": SERVER_NAME,
            "permintaan_total": None,
            "kunci": [],
            "pesan": _redis_error_message(exc),
        }), 503


@app.get("/slow")
def slow():
    """Permintaan lambat buatan.

    Dipakai untuk membuktikan proxy_connect_timeout / proxy_read_timeout di
    Nginx: permintaan yang melewati batas waktu dibuang (proxy_next_upstream
    timeout), bukan menggantung di klien.

    Durasi diambil dari ``?detik=`` bila ada, jika tidak dari SLOW_SECONDS.
    """
    from flask import request

    try:
        detik = float(request.args.get("detik", os.environ.get("SLOW_SECONDS", "2")))
    except ValueError:
        detik = 2.0
    detik = min(max(detik, 0.0), 30.0)
    time.sleep(detik)
    return jsonify({
        "server": SERVER_NAME,
        "tidur_detik": detik,
        "catatan": "permintaan lambat selesai dilayani",
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
