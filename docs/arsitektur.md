# Arsitektur Sistem

![Diagram arsitektur](diagrams/arsitektur-mkkl1030.png)

## Komponen

| Komponen | Peran | Port | Catatan |
|---|---|---|---|
| Nginx | Load balancer, satu-satunya pintu masuk | 80 | Membagi permintaan dan memeriksa kesehatan app server |
| app1 | App server Flask, salinan pertama | 5001 | Tanpa status sendiri |
| app2 | App server Flask, salinan kedua | 5002 | Kode identik dengan app1 |
| Redis | Penyimpanan status bersama | 6379 | Penyimpanan ulang AOF aktif |

## Alur Permintaan

1. Klien mengirim permintaan ke Nginx pada port 80. Klien tidak mengetahui jumlah app server di belakangnya.
2. Nginx memilih app server secara bergiliran (round-robin) dan meneruskan permintaan.
3. App server membaca atau menambah penghitung pada Redis, lalu membentuk respons.
4. Respons memuat identitas app server yang melayani, sehingga distribusi dapat dibuktikan dari sisi klien.
5. Nginx melakukan pemeriksaan kesehatan berkala; app server yang gagal dikeluarkan dari rotasi sampai kembali sehat.

## Keputusan Teknis

| Keputusan | Alasan |
|---|---|
| App server dibuat tanpa status sendiri | Agar app server dapat dimatikan kapan saja tanpa kehilangan data; seluruh status berada di Redis |
| Redis memakai AOF | Data ditulis ulang saat container dimulai ulang, sehingga ketahanan status dapat dibuktikan |
| Pemeriksaan kesehatan pada Nginx | Peralihan trafik terjadi otomatis, bukan hasil pemindahan manual |
| Respons memuat identitas app server | Menjadi bukti pemerataan beban dan peralihan yang dapat dilihat langsung |

## Titik Kegagalan yang Diketahui

Redis menjadi satu-satunya tempat status disimpan, sehingga ia sendiri menjadi
titik kegagalan tunggal. Kondisi ini dicatat secara terbuka pada laporan sebagai
bahan diskusi lanjutan — pengembangan berikutnya dapat menambahkan salinan
cadangan dengan mekanisme pengalihan otomatis.
