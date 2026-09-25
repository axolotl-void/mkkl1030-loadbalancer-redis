# Hasil Uji Kegagalan — MKKL1030

Catatan hasil setiap skenario pada `src/tests/uji_kegagalan.sh`.

**Cara menjalankan**

```bash
docker compose up --build -d
bash src/tests/uji_kegagalan.sh
```

**Lingkungan pengujian:** macOS, Docker Desktop, empat container pada satu mesin
(app1, app2, Redis, Nginx) — dijalankan pada *host* yang sama, bukan pada mesin
terpisah seperti pada penerapan sungguhan. Hal ini wajib disebutkan saat
melaporkan hasil, karena latensi dan throughput yang terukur tidak mewakili
jaringan sungguhan.

**Pembagian port:** Nginx `8080:80`, app1 `5001`, app2 `5002` (keduanya di dalam
jaringan `backend`, tidak dibuka ke *host*).

---

## Ringkasan hasil

| # | Skenario | Hasil | Bukti |
|---|---|---|---|
| 1 | Keadaan normal, 10 permintaan | Berhasil — app1 5 respons, app2 5 respons | `X-Served-By` dan isi respons |
| 2 | Beban tinggi 1000 permintaan, 50 bersamaan | Berhasil — 1000 respons HTTP 200 | Keluaran `hey` |
| 3 | app1 dimatikan saat sistem berjalan | Berhasil — 5 permintaan dijawab app2 seluruhnya, tanpa galat | Isi respons |
| 4 | Redis dimulai ulang | Berhasil — `permintaan_total` tidak hilang | `/state` sebelum dan sesudah |
| 5 | Permintaan 8 detik dengan batas baca 5 detik | Berhasil — klien menerima 504 pada detik ke-10 | Kode HTTP dan waktu tanggap |
| 6 | Redis dimatikan | Berhasil — app server tetap menjawab (HTTP 200), status kesehatan 503 | Isi respons dan `/health` |

---

## 1. Keadaan normal — 10 permintaan

```
{"permintaan_ke":10,"redis":"ok","server":"app2"}
{"permintaan_ke":11,"redis":"ok","server":"app1"}
{"permintaan_ke":12,"redis":"ok","server":"app2"}
...
{"permintaan_ke":19,"redis":"ok","server":"app1"}

  app1: 5 respons
  app2: 5 respons
```

Terlihat dua hal: Nginx membagi permintaan bergantian (bulat), dan
`permintaan_ke` naik terus **melintasi kedua app server** — bukti hitungan
disimpan di Redis, bukan di memori masing-masing proses.

## 2. Beban tinggi — 1000 permintaan, 50 bersamaan

```
Total:        0.1374 secs
Slowest:      0.0315 secs
Fastest:      0.0004 secs
Average:      0.0064 secs
Requests/sec: 7275.5007
Status code distribution:
  [200] 1000 responses
```

Tidak ada satu pun permintaan yang gagal. Pembagian beban diperiksa dari log
akses Nginx yang mencatat alamat *upstream* setiap permintaan:

```
508  upstream=172.20.0.3:5001   (app1)
511  upstream=172.20.0.4:5002   (app2)
```

Selisih 508 banding 511 dari 1019 permintaan — perbedaan 0,3%, jadi
penyeimbangannya terbagi rata. Angka ini jauh lebih kuat sebagai bukti
dibanding sekadar menyebut "round-robin" pada konfigurasi.

## 3. app1 dimatikan saat sistem berjalan

```
  app2: 5 respons
```

Seluruh permintaan tetap dijawab dan tidak ada yang gagal. Nginx mengenali app1
mati (`max_fails=2`, `fail_timeout=10s`) lalu mengarahkan semua permintaan ke
app2. Setelah `docker compose start app1`, app1 kembali masuk perputaran.

## 4. Redis dimulai ulang

```
sebelum: {"kunci":["permintaan_total"],"permintaan_total":"24","server":"app2"}
sesudah: {"kunci":["permintaan_total"],"permintaan_total":"24","server":"app1"}
  nilai permintaan_total bertahan
```

Nilai 24 tetap sama setelah Redis dimulai ulang. Penyebabnya `--appendonly yes`
pada `docker-compose.yml`: Redis menuliskan setiap perubahan ke berkas di dalam
volume `redis-data`, sehingga data tidak hilang saat prosesnya berhenti.

## 5. Batas waktu baca — permintaan 8 detik

Klien memanggil `/slow?detik=8`; Nginx memakai `proxy_read_timeout 5s`.

```
  kode HTTP: 504
  waktu tanggap klien: 10067 ms
```

Perlu dijelaskan apa adanya: klien menerima **504 setelah ±10 detik**, bukan 5
detik. Sebabnya, Nginx mencoba **dua** node (`proxy_next_upstream_tries 2`),
masing-masing menunggu 5 detik sebelum dianggap lewat batas waktu. Jadi 5 detik
+ 5 detik ≈ 10 detik, lalu Nginx menyerah dan mengembalikan 504.

Uji ini membuktikan batas waktu bekerja: tanpa `proxy_read_timeout`, permintaan
akan menggantung tanpa batas. Untuk pemakaian sungguhan, harga 10 detik itu
terlalu lama untuk layanan yang melayani banyak permintaan — perbaikan yang
disarankan adalah `proxy_next_upstream_timeout` (sudah dipasang 12 detik
sebagai batas keseluruhan) dan menurunkan `proxy_read_timeout` bila layanan
memang harus cepat.

## 6. Redis dimatikan

```
--- permintaan saat Redis mati ---
  kode HTTP: 200
  isi: {"permintaan_ke":null,"pesan":"Redis tidak dapat dihubungi (ConnectionError)","redis":"gagal","server":"app1"}

--- status kesehatan ---
  kode HTTP: 503
```

Dua perilaku yang sengaja dibedakan:

- **Permintaan biasa tetap dilayani (200).** Redis mati bukan alasan menolak
  pengguna — app server menjawab dengan `"redis":"gagal"` dan
  `"permintaan_ke":null` supaya keadaannya jujur terlihat, bukan berpura-pura
  berhasil.
- **Status kesehatan menjadi 503.** Pemeriksaan kesehatan menganggap Redis
  wajib, sehingga Nginx akan membuang node tanpa penyimpanan bersama dari
  perputaran permintaan. Kalau `/health` tetap menjawab 200, Nginx akan terus
  mengirim permintaan ke node yang tidak dapat memenuhi fungsinya.

`proxy_connect_timeout` dan `socket_connect_timeout` yang pendek (1–2 detik)
penting di sini: tanpa keduanya, permintaan akan menggantung lama menunggu
Redis yang sudah mati.
