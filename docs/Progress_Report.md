# VC Ratio Monitoring System

## Development Progress Report

---

## Developer

**Nama :** Eggi Chandra

**Project :** VC Ratio Monitoring System

**Repository :**
https://github.com/chandra527/VC-Ratio-Monitoring-System

---

# Tujuan Project

Membangun sistem monitoring lalu lintas berbasis Computer Vision menggunakan OpenCV dan YOLOv8 untuk menghitung volume kendaraan, menghitung VC Ratio, menyimpan data ke CSV dan Database, serta dipersiapkan untuk implementasi pada server Dishub.

---

# Arsitektur Project

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
        ▼
Vehicle Counting
        │
        ▼
Traffic Analysis
        │
        ├──────────────► CSV Logger
        │
        └──────────────► SQLite Database
```

---

# Sprint 1

## Environment Preparation

### Target

- Install VS Code
- Install Python
- Install OpenCV
- Membaca video CCTV

### Hasil

✅ Berhasil menjalankan video .dav menggunakan OpenCV.

---

# Sprint 2

## YOLO Vehicle Detection

### Target

Deteksi kendaraan menggunakan YOLOv8.

### Hasil

✅ Berhasil mendeteksi:

- Motor
- Mobil
- Bus
- Truk
- Ambulans

---

# Sprint 3

## ByteTrack

### Target

Memberikan Tracking ID pada kendaraan.

### Hasil

Contoh:

```
Mobil #4
Motor #12
Truk #8
```

Tracking berhasil berjalan menggunakan ByteTrack.

---

# Sprint 4

## Vehicle Counting

### Target

Menghitung kendaraan yang melewati garis.

### Hasil

Menggunakan konsep:

- Stable Tracking
- Class Voting
- Seen Above
- Crossed ID

Output:

```
TERHITUNG:

Motor ID #15
Mobil ID #8
```

---

# Sprint 5

## Dashboard Monitoring

### Target

Dashboard monitoring profesional.

### Hasil

Dashboard berhasil menampilkan:

- Live Traffic Camera
- Vehicle Count
- Traffic Analysis
- VC Ratio
- FPS
- Resolution

---

# Sprint 6

## CSV Logger

### Target

Menyimpan data lalu lintas setiap interval.

### Hasil

Berhasil membuat

```
output/traffic_log.csv
```

Contoh:

timestamp,motor,mobil,bus,...

Data tersimpan otomatis setiap 60 detik.

---

# Sprint 7

## SQLite Database

### Target

Menyimpan data lalu lintas ke database.

### Hasil

Berhasil membuat

```
traffic_data.db
```

Data berhasil masuk ke tabel SQLite.

---

# Refactoring

Selama pengembangan dilakukan beberapa refactoring:

- Dashboard dipisah menjadi beberapa module.
- Tracking dipisah dari YOLO Detector.
- Vehicle Counting dipindahkan ke class VehicleTracker.
- CSV Logger dipisahkan menjadi module sendiri.
- Database Logger dipisahkan menjadi module sendiri.

Tujuan refactoring:

- Mempermudah maintenance.
- Mempermudah debugging.
- Mempermudah pengembangan fitur baru.

---

# GitHub

Repository telah berhasil menggunakan Git.

Commit dilakukan secara bertahap mengikuti setiap milestone.

Contoh:

```
feat: stable dashboard

feat: add tracking

feat: add vehicle counting

feat: add CSV logging

feat: add SQLite logging
```

---

# Kendala

Selama proses pengembangan ditemukan beberapa kendala:

- Tracking ID sering berubah.
- Label kendaraan berubah.
- Counting ganda.
- Dashboard beberapa kali di-refactor.
- GitHub gagal push karena ukuran file video.
- DNS GitHub sempat gagal.

Semua berhasil diselesaikan.

---

# Progress Saat Ini

| Modul | Status |
|--------|--------|
| OpenCV Streaming | ✅ |
| YOLO Detection | ✅ |
| ByteTrack | ✅ |
| Vehicle Counting | ✅ |
| Dashboard | ✅ |
| VC Ratio | ✅ |
| CSV Logger | ✅ |
| SQLite Database | ✅ |
| GitHub | ✅ |
| Speed Estimation | ⏳ |
| Server Deployment | ⏳ |

---

# Roadmap Berikutnya

1. Speed Estimation
2. Persiapan Server
3. TeamViewer Remote
4. Live CCTV
5. Database Online

---

# Catatan

Project dikembangkan mengikuti workflow:

```
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
```

Workflow tersebut digunakan agar setiap perubahan terdokumentasi dan mudah dikembangkan kembali.