# Hasil Uji Kegagalan

Catatan hasil setiap skenario pengujian. Tabel diisi bertahap sepanjang semester
dan dilengkapi menjelang UAS.

## Alat dan Cara Uji

```bash
# Menjalankan seluruh sistem
docker compose up --build -d

# Menguji beban (perlu: brew install hey)
hey -n 1000 -c 50 http://localhost/

# Skrip lengkap keempat skenario
bash src/tests/uji_kegagalan.sh
```

## 1. Keadaan Normal

Yang diperiksa: permintaan terbagi merata ke kedua app server.

| Sesi | Waktu | Jumlah permintaan | app1 | app2 | Selisih | Catatan |
|---|---|---|---|---|---|---|
| Normal #1 | Belum diuji | — | — | — | — | — |

## 2. Satu App Server Dimatikan

Yang diperiksa: layanan tetap merespons dan berapa lama peralihannya.

| Sesi | App yang dimatikan | Permintaan saat mati | Berhasil | Gagal | Waktu peralihan | Catatan |
|---|---|---|---|---|---|---|
| Uji #1 | app1 | Belum diuji | — | — | — | — |

## 3. Beban Tinggi

Yang diperiksa: distribusi permintaan tetap merata dan sistem tidak berhenti.

| Sesi | Jumlah permintaan | Bersamaan | Berhasil | Gagal | Waktu rata-rata | Permintaan/detik |
|---|---|---|---|---|---|---|
| Beban #1 | 1000 | 50 | — | — | — | — |

## 4. Restart Penyimpanan Bersama

Yang diperiksa: status bersama tetap utuh setelah container dimulai ulang.

| Sesi | Nilai sebelum restart | Nilai sesudah restart | Utuh? | Catatan |
|---|---|---|---|---|
| Restart #1 | Belum diuji | — | — | — |

## Temuan Sementara

Belum ada temuan — pengujian dimulai pada minggu ke-6.

## Catatan Pelaksanaan

Setiap sesi dicatat pula: spesifikasi perangkat yang dipakai, versi Docker,
dan waktu pengujian. Hasil antar-perangkat dibandingkan secara kualitatif,
bukan sebagai angka mutlak, karena spesifikasi perangkat memengaruhi hasil
pengujian beban.
