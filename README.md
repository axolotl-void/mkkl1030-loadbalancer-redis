# Load Balancer dan Replicated App — Sistem Tiga Container dengan Nginx, Flask, dan Redis

**Mata kuliah:** Sistem Paralel dan Terdistribusi (MKKL1030) · Semester 7
**Program Studi Ilmu Komputer — Fakultas Sains, Teknologi dan Ilmu Kesehatan**
**Universitas Bina Bangsa Getsempena**
**Dosen Pengampu:** Ahmad Mujahid Abdurrahman, S.Kom, M.T.

Purwarupa sistem terdistribusi berisi empat container Docker: Nginx sebagai load balancer, dua app server Flask yang identik, dan Redis sebagai penyimpanan status bersama. Klien hanya mengenal satu alamat, sementara Nginx membagi permintaan ke kedua app server dan memeriksa kesehatannya secara berkala. Sistem ini diuji dengan mematikan salah satu app server saat permintaan sedang berjalan, memberi beban tinggi, dan memulai ulang penyimpanan bersama, untuk membuktikan toleransi kegagalan serta konsistensi data.

## Anggota Kelompok

| No | Nama | NIM | Peran |
|---|---|---|---|
| 1 | Yogi Prasetya Sadewa | 23210060 | Ketua kelompok; berkas Docker Compose, konfigurasi Nginx, dan skenario pengujian kegagalan |
| 2 | [Nama Anggota 2] | [NIM] | Aplikasi Flask dan titik akhir pemeriksaan kesehatan |
| 3 | [Nama Anggota 3] | [NIM] | Konfigurasi Redis sebagai penyimpanan status bersama dan pengujian ketahanan data |
| 4 | [Nama Anggota 4] | [NIM] | Penyiapan lingkungan Docker dan pembuatan berkas image |
| 5 | [Nama Anggota 5] | [NIM] | Pengujian beban dan pencatatan hasil pengalihan trafik |
| 6 | [Nama Anggota 6] | [NIM] | Dokumentasi, README, dan pengelolaan repository |

> Kelompok berisi 6 orang. Bagian yang belum memiliki nama akan dilengkapi pada
> pertemuan berikutnya; setiap anggota melakukan commit dari akun masing-masing.

## Rencana Proyek

- Google Docs (dibagikan kepada dosen dengan akses komentar) — tautan: `[ISI TAUTAN]`
- Salinan di repository: [`docs/rencana-proyek.md`](docs/rencana-proyek.md)

## Cara Menjalankan

### Kebutuhan

- Docker dan Docker Compose
- Perkakas uji beban (opsional): hey atau ApacheBench

### 1. Menjalankan seluruh sistem

```bash
docker compose up --build -d
docker compose ps
```

### 2. Menguji layanan melalui load balancer

```bash
# Perhatikan field "server" pada respons: bergantian antara app1 dan app2
curl -s http://localhost/ | jq
```

### 3. Menguji kegagalan satu app server

```bash
docker compose stop app1
curl -s http://localhost/ | jq   # harus tetap dijawab app2
docker compose start app1
```

### 4. Menguji beban dan ketahanan status

```bash
hey -n 1000 -c 50 http://localhost/
docker compose restart redis
curl -s http://localhost/state | jq
```

> Bagian yang belum selesai ditandai `TODO` beserta minggu pengerjaannya.

## Struktur Repository

```
mkkl1030-loadbalancer-redis/
├── README.md
├── docker-compose.yml
├── docs/
│   ├── rencana-proyek.md
│   ├── arsitektur.md
│   ├── hasil-uji-kegagalan.md
│   ├── diagrams/
│   └── MKKL1030-Load-Balancer-Replicated-App.docx
├── src/
│   ├── app/             # aplikasi Flask (dipakai kedua container)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── tests/           # skrip pengujian beban dan kegagalan
└── nginx/
    └── nginx.conf       # pengaturan upstream + health check
```

## Dokumentasi

| Berkas | Isi |
|---|---|
| `docs/rencana-proyek.md` | Rencana proyek, target UTS dan UAS, pembagian kerja per minggu, risiko |
| `docs/arsitektur.md` | Penjelasan komponen, alur permintaan, dan keputusan teknis |
| `docs/hasil-uji-kegagalan.md` | Catatan hasil setiap skenario pengujian kegagalan |
| `docs/diagrams/` | Diagram arsitektur dan alur permintaan |

## Pemenuhan Ketentuan Mata Kuliah

- **Minimal dua proses terpisah**: empat container yang saling berkomunikasi melalui jaringan Docker.
- **Mekanisme komunikasi**: HTTP antar-container dan protokol Redis untuk penyimpanan status bersama.
- **Isu terdistribusi yang ditangani**: penyeimbangan beban, replikasi dan konsistensi status, serta toleransi kegagalan.
- **Skenario uji kegagalan**: mematikan app server saat beban berjalan dan memulai ulang penyimpanan bersama.

## Aturan Kerja Kelompok

- Commit dilakukan dari akun GitHub masing-masing anggota, bukan satu akun untuk seluruh kelompok.
- Pesan commit deskriptif dan menunjukkan kemajuan; dikerjakan minimal sekali per minggu per anggota.
- Pekerjaan bersama menggunakan branch dan pull request; pembagian tugas dicatat pada Issues.
- Kredensial, token, dan berkas `.env` tidak boleh masuk repository.

## Status

| Tahap | Target | Status |
|---|---|---|
| Pertemuan 2 | Rencana proyek, repository, undangan kolaborator | Selesai |
| Pertemuan 8 (UTS) | Seluruh container berjalan dan klien dapat mengakses layanan melalui load balancer … | Belum dimulai |
| Pertemuan 16 (UAS) | Sistem tiga komponen yang berjalan penuh dan dapat dijalankan ulang dari satu berkas Compo … | Belum dimulai |
