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

TODO(minggu 3): lengkapi titik akhir dan penanganan kegagalan Redis.
"""
from __future__ import annotations

import os

from flask import Flask, jsonify
import redis

app = Flask(__name__)

SERVER_NAME = os.environ.get("SERVER_NAME", "app?")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


@app.get("/")
def index():
    try:
        total = r.incr("permintaan_total")
    except redis.RedisError:
        # TODO(minggu 3): tangani ketidaktersediaan Redis dengan rapi.
        total = -1
    return jsonify({"server": SERVER_NAME, "permintaan_ke": total})


@app.get("/health")
def health():
    return jsonify({"status": "ok", "server": SERVER_NAME}), 200


@app.get("/state")
def state():
    return jsonify({
        "server": SERVER_NAME,
        "permintaan_total": r.get("permintaan_total"),
        "kunci": sorted(r.keys("*")),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
