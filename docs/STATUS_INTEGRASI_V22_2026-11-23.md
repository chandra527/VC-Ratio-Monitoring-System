# Integrasi Python/YOLO dengan VC-Ratio Web V2.2

**Dicatat:** 23 November 2026. **Basis:** pengujian dan audit dokumentasi yang dilaporkan, bukan pembacaan ulang seluruh source.

## Alur

1. Video realtime dari dua kamera diproses oleh pipeline Python untuk deteksi YOLO, tracking ByteTrack, virtual gate, speed dan perhitungan V/C.
2. Monitoring Laravel menampilkan kondisi lalu lintas dan ringkasan; sumber nilai live dan record database harus dipisahkan dalam analisis.
3. Offline Analyzer web menerima hanya file rekaman yang diizinkan profil backend, menjalankan `testing/offline_video_analyzer_v2.py` melalui worker CLI terjadwal, lalu membaca JSON/CSV dan video anotasi opsional.
4. Modul offline tidak menulis hasil counting rekaman ke tabel trafik produksi realtime.

## Uji video 30 detik

| Kamera | Counting web | Speed baseline Python | Catatan |
|---|---:|---:|---|
| Jl. Pattimura | 20 | 18 | Jarak speed referensi 8 m |
| Jl. Jenderal Urip | 17 | 15 | Jarak speed 10 m perkiraan; belum validasi lapangan |

Pekerjaan kedua kamera dilaporkan berstatus `SELESAI` di web pada 22 November 2026. Tidak dibuat video anotasi dalam job regresi tersebut.

## Risiko dan pekerjaan tertunda

- Pengukuran kecepatan wajib divalidasi terhadap pengamatan independen dan geometri yang tepat; label arah virtual gate tidak otomatis sama dengan arah geografis jalan.
- ID switch ByteTrack di Urip dapat menyebabkan kendaraan terlewat atau kehilangan pasangan speed; jangan mengklaim akurasi penuh.
- Sejumlah perubahan `src/main.py`, `src/speed_estimator.py` dan modul lain belum di-commit pada audit; baca diff dulu sebelum menggabungkan/perbarui environment realtime.
- Folder `testing/` berisi kode aktif Offline Analyzer; **hanya keluaran hasilnya** yang boleh dikecualikan secara default dari Git.
- Dokumentasi arsitektur dan progress lama memuat tahapan SQLite serta roadmap RTSP sebelum V2.2; catatan tersebut dipertahankan sebagai histori, bukan penjelasan server terkini.

## Rujukan lintas repositori

- Laravel: `docs/STATUS_V22_2026-11-23.md` dan `docs/Dokumentasi_Offline_Analyzer_VC_Ratio_V2.md`.
- Python: `docs/Architecture.md`, `docs/Progress_Report.md`, `CHANGELOG.md`.
