# VC Ratio Monitoring System

## Development Progress Report

---

## Developer

**Nama:** Eggi Chandra  
**Project:** VC Ratio Monitoring System  
**Repository:**  
https://github.com/chandra527/VC-Ratio-Monitoring-System

---

# Tujuan Project

Membangun sistem monitoring lalu lintas berbasis Computer Vision menggunakan OpenCV dan YOLOv8 untuk:

- mendeteksi kendaraan,
- melakukan tracking kendaraan,
- menghitung volume kendaraan,
- menghitung VC Ratio,
- mengestimasi kecepatan kendaraan,
- menampilkan dashboard monitoring,
- menyimpan data ke CSV,
- menyimpan data ke SQLite Database,
- serta mempersiapkan aplikasi untuk implementasi pada server Dishub.

---

# Arsitektur Project

```text
Video CCTV (.dav)
        │
        ▼
OpenCV Video Capture
        │
        ▼
YOLOv8 Detection
        │
        ▼
ByteTrack Tracking
        │
        ├──────────────► VehicleTracker
        │                 Vehicle Counting
        │
        └──────────────► SpeedEstimator
                          Speed Estimation
        │
        ▼
Traffic Analysis
        │
        ├──────────────► Dashboard
        ├──────────────► CSV Logger
        └──────────────► SQLite Database
```

---

# Sprint 1

## Environment Preparation

### Target

- Install Visual Studio Code
- Install Python
- Install OpenCV
- Membaca video CCTV

### Hasil

✅ Visual Studio Code dan Python berhasil dipasang.  
✅ OpenCV berhasil dijalankan.  
✅ Video CCTV dengan format `.dav` berhasil dibaca dan ditampilkan.

---

# Sprint 2

## YOLO Vehicle Detection

### Target

Mengintegrasikan YOLOv8 untuk mendeteksi kendaraan dari video CCTV.

### Hasil

✅ Model YOLOv8 berhasil dijalankan.

Jenis kendaraan yang diproses:

- Motor
- Mobil
- Bus
- Truk
- Ambulans

Fitur yang berhasil dibuat:

- Bounding box
- Label kendaraan
- Confidence detection
- Filter kelas kendaraan

---

# Sprint 3

## ByteTrack Multi Object Tracking

### Target

Memberikan Tracking ID pada setiap kendaraan agar kendaraan yang sama dapat dikenali pada beberapa frame.

### Hasil

✅ ByteTrack berhasil dijalankan menggunakan `model.track()`.

Contoh label:

```text
Mobil #4
Motor #12
Truk #8
```

### Kendala

- Tracking ID terkadang hilang.
- ID dapat berubah saat kendaraan tertutup objek lain.
- Motor yang berukuran kecil lebih sulit dipertahankan ID-nya.

### Penanganan

- Menggunakan `persist=True`.
- Menyesuaikan confidence YOLO.
- Menggunakan ukuran inference yang lebih besar.
- Membatasi kelas yang diproses.

---

# Sprint 4

## Vehicle Counting

### Target

Menghitung kendaraan yang benar-benar memasuki counting zone dan mencegah penghitungan berulang.

### Hasil

✅ Vehicle Counting berhasil dibuat menggunakan class:

```text
VehicleTracker
```

Konsep yang digunakan:

- Stable Tracking
- Class Voting
- Seen Above
- Crossed ID
- Counting Zone
- Duplicate Prevention

Contoh output:

```text
TERHITUNG: motor ID #15 Total = 1
TERHITUNG: mobil ID #8 Total = 1
```

### Kendala

- Label kendaraan dapat berubah antara mobil, bus, dan truk.
- Tracking ID yang terputus dapat menghasilkan ID baru.
- Penghitungan motor lebih sulit karena ukuran objek kecil.

### Penanganan

- Menggunakan voting jenis kendaraan dengan `Counter`.
- Menetapkan minimal kemunculan ID.
- Menggunakan zona toleransi, bukan hanya satu garis tipis.

---

# Sprint 5

## Dashboard Monitoring

### Target

Membuat dashboard yang mampu menampilkan video dan hasil analisis lalu lintas secara realtime.

### Hasil

✅ Dashboard berhasil menampilkan:

- Live Traffic Camera
- Bounding box dan Tracking ID
- Counting Zone
- Vehicle Count
- Traffic Volume
- Capacity
- VC Ratio
- Traffic Status
- Frame number
- FPS
- Resolution

### Refactoring Tampilan

Dashboard awal memiliki dua video:

- Camera View
- Image Processing

Kemudian tampilan diubah menjadi satu kamera utama yang lebih besar agar lebih sesuai dengan kebutuhan monitoring CCTV.

---

# Sprint 6

## CSV Logger

### Target

Menyimpan data lalu lintas secara periodik ke file CSV.

### Hasil

✅ Berhasil membuat modul:

```text
src/csv_logger.py
```

Output:

```text
output/traffic_log.csv
```

Struktur data:

```text
timestamp,motor,mobil,bus,truk,ambulans,total,capacity,vc_ratio,status
```

Data disimpan otomatis setiap interval waktu yang ditentukan.

Contoh log terminal:

```text
CSV TERSIMPAN: 2026-07-16 11:25:09
```

---

# Sprint 7

## SQLite Database

### Target

Menyimpan data lalu lintas ke database lokal.

### Hasil

✅ Berhasil membuat modul:

```text
src/database_logger.py
```

Output database:

```text
output/traffic_data.db
```

Tabel utama:

```text
traffic_logs
```

Data yang disimpan:

- Timestamp
- Motor
- Mobil
- Bus
- Truk
- Ambulans
- Total
- Capacity
- VC Ratio
- Status

Contoh log terminal:

```text
DATABASE TERSIMPAN: 2026-07-16 11:25:09
```

---

# Sprint 8

## Speed Estimation

### Target

Mengestimasi kecepatan kendaraan menggunakan dua garis virtual dan Tracking ID.

### Desain

Speed Estimation dibuat sebagai modul terpisah:

```text
src/speed_estimator.py
```

Modul ini tidak digabungkan dengan `VehicleTracker`, sehingga error pada Speed Estimator tidak merusak Vehicle Counting.

Arsitektur:

```text
Tracking Result
        │
        ├──────────────► VehicleTracker
        │                 Vehicle Counting
        │
        └──────────────► SpeedEstimator
                          Speed Estimation
```

### Metode Perhitungan

Speed Estimator menggunakan:

- Tracking ID
- Frame saat kendaraan melewati Line A
- Frame saat kendaraan mencapai Line B
- FPS asli video
- Asumsi jarak nyata 10 meter

Perhitungan waktu:

```text
Waktu tempuh = selisih frame / FPS
```

Perhitungan kecepatan:

```text
Kecepatan m/s = jarak / waktu tempuh

Kecepatan km/jam = kecepatan m/s × 3,6
```

### Hasil

✅ Speed Estimation berhasil berjalan.

Contoh output:

```text
SPEED LINE A: mobil ID #44 Frame 127

KECEPATAN ESTIMASI:
mobil ID #44
26.5 km/jam
1.36 detik
```

Contoh lain:

```text
KECEPATAN ESTIMASI: motor ID #54 23.7 km/jam
KECEPATAN ESTIMASI: motor ID #83 27.3 km/jam
```

### Catatan

Nilai kecepatan masih berupa estimasi karena jarak 10 meter belum dikalibrasi langsung di lokasi CCTV.

---

# Refactoring

Selama pengembangan dilakukan beberapa refactoring.

## Pemisahan Modul

- Dashboard dipisah menjadi `layout.py` dan `draw.py`.
- Tracking dipisahkan dari YOLO Detector.
- Vehicle Counting dipindahkan ke class `VehicleTracker`.
- Speed Estimation dibuat sebagai class `SpeedEstimator`.
- CSV Logger dibuat sebagai modul terpisah.
- Database Logger dibuat sebagai modul terpisah.

## Tujuan Refactoring

- Mempermudah maintenance.
- Mempermudah debugging.
- Mencegah satu fitur merusak fitur lain.
- Mempermudah pengembangan fitur baru.
- Mempersiapkan aplikasi untuk deployment server.

---

# Git dan GitHub

Repository telah berhasil menggunakan Git dan GitHub.

Commit dibuat secara bertahap mengikuti setiap milestone.

Contoh commit:

```text
feat: add vehicle counting zone and class voting

fix: restore stable vehicle counting zone

feat: add periodic traffic CSV logging

feat: add SQLite traffic data logging

docs: add project architecture and progress report
```

Repository:

```text
https://github.com/chandra527/VC-Ratio-Monitoring-System
```

---

# Kendala yang Ditemui

Selama proses pengembangan ditemukan beberapa kendala:

- Tracking ID sering berubah atau hilang.
- Label kendaraan berubah antara mobil, bus, dan truk.
- Kendaraan berpotensi dihitung lebih dari satu kali.
- Motor kecil lebih sulit dilacak.
- Dashboard beberapa kali mengalami perubahan layout.
- File video melebihi batas ukuran GitHub.
- Model YOLO dan video tidak boleh ikut repository.
- GitHub sempat gagal diakses karena masalah DNS.
- Implementasi Speed Estimation pertama merusak counting dan harus di-rollback.

---

# Solusi yang Diterapkan

- Menggunakan ByteTrack dengan `persist=True`.
- Menggunakan class voting.
- Menggunakan `crossed_ids`.
- Menggunakan counting zone dengan toleransi.
- Memisahkan Speed Estimator dari Vehicle Tracker.
- Menambahkan `.gitignore`.
- Menghapus file video dan model dari riwayat Git.
- Membuat ulang repository Git lokal.
- Menggunakan Git commit sebagai dokumentasi perubahan.
- Melakukan rollback ketika fitur baru mengganggu versi stabil.

---

# Progress Saat Ini

| Modul | Status |
|---|:---:|
| OpenCV Streaming | ✅ |
| YOLOv8 Detection | ✅ |
| ByteTrack | ✅ |
| Vehicle Counting | ✅ |
| Counting Zone | ✅ |
| Dashboard | ✅ |
| Traffic Volume | ✅ |
| VC Ratio | ✅ |
| Traffic Status | ✅ |
| CSV Logger | ✅ |
| SQLite Database | ✅ |
| Speed Estimation | ✅ |
| GitHub | ✅ |
| Project Documentation | ✅ |
| Speed Overlay | ⏳ |
| Average Speed Dashboard | ⏳ |
| Server Deployment | ⏳ |
| Live CCTV / RTSP | ⏳ |

---

# Roadmap Berikutnya

1. Speed Overlay pada bounding box
2. Average Speed Dashboard
3. Penyimpanan data kecepatan ke CSV dan database
4. Persiapan instalasi server
5. Running test pada server
6. Integrasi CCTV live menggunakan RTSP
7. Database online
8. Web Dashboard

---

# Workflow Pengembangan

Project dikembangkan mengikuti workflow:

```text
Analisis
    ↓
Dokumentasi
    ↓
Review
    ↓
Coding
    ↓
Update Dokumentasi
    ↓
Testing
    ↓
Git Commit
```

Workflow ini digunakan agar setiap perubahan:

- terdokumentasi,
- dapat ditinjau kembali,
- mudah diuji,
- dan dapat dikembalikan ke versi stabil apabila terjadi error.

---

# Versi Saat Ini

```text
Version 0.8
```

Milestone Version 0.8:

- Vehicle Detection
- Multi Object Tracking
- Vehicle Counting
- VC Ratio
- Dashboard Monitoring
- CSV Logger
- SQLite Database
- Speed Estimation