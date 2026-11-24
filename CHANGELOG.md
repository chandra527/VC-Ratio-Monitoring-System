# Changelog — VC-Ratio Python / YOLO

Tanggal di bawah berasal dari pengujian yang dilaporkan; tidak menyiratkan sudah di-commit atau di-push.

## [Unreleased] — Status lokal 23 November 2026

### 22–23 November 2026

- Mendukung alur pengujian offline dua rekaman melalui integrasi Laravel: Pattimura dan Jenderal Urip (masing-masing counting web 30 detik: 20 dan 17).
- Referensi baseline Python 30 detik: Pattimura 18 pengukuran speed; Jenderal Urip 15.
- Geometri speed/counting per rekaman ditetapkan dalam profil backend Laravel, tidak disamakan antar-kamera.
- Hasil analisis offline tetap dipisahkan dari pipeline statistik realtime.

### Known limitations

- Tracking Jenderal Urip dapat mengalami peralihan ID pada objek yang sama (*ID switch*), memengaruhi counting dan pairing speed. Eksperimen resolusi/konfigurasi tidak membuktikan perbaikan konsisten; tidak ada perubahan algoritma produksi yang disetujui untuk masalah ini.
- Referensi jarak speed Jenderal Urip 10 m belum diverifikasi di lapangan. Estimasi kecepatan tidak boleh dipresentasikan sebagai pengukuran resmi.
- Status repositori pada audit: `feature/multi-camera` berada `ahead 9` terhadap remote-tracking lokal, tetapi belum diverifikasi setelah fetch.

Catatan: isi changelog tidak menyatakan bahwa seluruh perubahan `src/` sudah lulus regresi; kode offline dan realtime harus diaudit terpisah sebelum release.
