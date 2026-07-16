# VC Ratio Monitoring System

## System Architecture

Dokumen ini menjelaskan struktur aplikasi, hubungan antar-modul, tanggung jawab setiap komponen, serta aliran data pada project **VC Ratio Monitoring System**.

---

# 1. Tujuan Arsitektur

Arsitektur project dibuat modular agar:

- setiap bagian mempunyai tanggung jawab yang jelas,
- proses debugging lebih mudah,
- fitur baru dapat ditambahkan tanpa merusak fitur lama,
- kode lebih mudah dibaca dan dipelihara,
- perubahan dapat diuji secara terpisah,
- aplikasi lebih siap dipindahkan ke server.

---

# 2. Gambaran Umum Sistem

```text
Video CCTV
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
    │                 ├── Vehicle Counting
    │                 ├── Class Voting
    │                 └── Duplicate Prevention
    │
    └──────────────► SpeedEstimator
                      ├── Line A Crossing
                      ├── Line B Crossing
                      ├── Travel Time
                      └── Speed Estimation
    │
    ▼
Traffic Analysis
    │
    ├── Volume
    ├── Capacity
    ├── VC Ratio
    └── Traffic Status
    │
    ├──────────────► Dashboard
    ├──────────────► CSV Logger
    └──────────────► SQLite Database
```

---

# 3. Struktur Folder

```text
VC_RATIO_PROJECT_NEW
│
├── data/
│   └── pak_kasih.dav
│
├── models/
│   └── yolov8n.pt
│
├── output/
│   ├── traffic_log.csv
│   └── traffic_data.db
│
├── docs/
│   ├── Progress_Report.md
│   └── Architecture.md
│
├── src/
│   ├── main.py
│   ├── layout.py
│   ├── draw.py
│   ├── processing.py
│   ├── utils.py
│   ├── yolo_detector.py
│   ├── tracker.py
│   ├── vehicle_tracker.py
│   ├── line_counter.py
│   ├── speed_estimator.py
│   ├── csv_logger.py
│   └── database_logger.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

Catatan:

- Folder `data/` berisi video uji lokal dan tidak disimpan ke GitHub.
- Folder `models/` berisi model YOLO dan tidak disimpan ke GitHub.
- File hasil pada folder `output/` dapat diabaikan dari repository apabila hanya digunakan sebagai data runtime.

---

# 4. Tanggung Jawab Setiap Modul

## `main.py`

Berfungsi sebagai pusat koordinasi alur aplikasi.

Tugas utama:

- membuka video,
- membaca frame,
- memanggil YOLO dan ByteTrack,
- memperbarui vehicle count,
- memperbarui speed estimation,
- menghitung data lalu lintas,
- menggambar frame dan dashboard,
- menyimpan data ke CSV,
- menyimpan data ke database,
- menampilkan aplikasi.

Alur utama:

```text
Read Frame
    ↓
Track Vehicles
    ↓
Update VehicleTracker
    ↓
Update SpeedEstimator
    ↓
Update Traffic Data
    ↓
Save CSV and Database
    ↓
Draw Detection and Dashboard
    ↓
Display
```

`main.py` berperan sebagai penghubung modul, bukan tempat seluruh logika fitur ditulis.

---

## `yolo_detector.py`

Bertanggung jawab terhadap konfigurasi dan hasil deteksi kendaraan.

Tugas:

- memuat model YOLOv8,
- membaca nama kelas YOLO,
- memetakan kelas YOLO ke jenis kendaraan aplikasi,
- menggambar bounding box,
- menggambar label kendaraan.

Contoh pemetaan kelas:

```python
VEHICLE_CLASSES = {
    "motorcycle": {
        "label": "Motor",
        "key": "motor"
    },
    "car": {
        "label": "Mobil",
        "key": "mobil"
    },
    "bus": {
        "label": "Bus",
        "key": "bus"
    },
    "truck": {
        "label": "Truk",
        "key": "truk"
    }
}
```

---

## `tracker.py`

Bertanggung jawab menjalankan tracking kendaraan menggunakan ByteTrack.

Tugas:

- menerima frame,
- menjalankan `model.track()`,
- mempertahankan tracking ID antar-frame,
- membatasi kelas kendaraan yang diproses,
- mengembalikan hasil tracking.

Contoh:

```python
results = model.track(
    frame,
    persist=True,
    tracker="bytetrack.yaml",
    verbose=False
)
```

Output utama modul ini adalah hasil tracking yang berisi:

- bounding box,
- class ID,
- confidence,
- tracking ID.

---

## `vehicle_tracker.py`

Berfungsi sebagai mesin penghitungan kendaraan.

Tugas utama:

- menyimpan jumlah kemunculan tracking ID,
- memastikan tracking cukup stabil,
- melakukan voting kelas kendaraan,
- mendeteksi kendaraan yang memasuki counting zone,
- mencegah kendaraan dihitung dua kali,
- menyimpan jumlah kendaraan berdasarkan jenis.

Data penting di dalam class:

```text
track_frames
class_votes
seen_above
crossed_ids
vehicle_count
```

Alur kendaraan:

```text
Object Detected
    ↓
Tracking ID Available?
    ↓
Vehicle Class Valid?
    ↓
Class Voting
    ↓
Seen Above Counting Zone?
    ↓
Entered Counting Zone?
    ↓
Track Stable?
    ↓
Already Counted?
    ↓
Counter +1
```

`VehicleTracker` tidak menghitung kecepatan.

Pemisahan ini menjaga agar fitur counting tetap stabil ketika fitur speed dikembangkan.

---

## `speed_estimator.py`

Berfungsi sebagai mesin estimasi kecepatan kendaraan.

Tugas utama:

- membaca tracking ID,
- mengingat posisi Y kendaraan pada frame sebelumnya,
- mendeteksi kendaraan melewati Line A,
- mencatat nomor frame pada Line A,
- mendeteksi kendaraan melewati Line B,
- menghitung waktu tempuh,
- menghitung estimasi kecepatan dalam km/jam,
- menyimpan kecepatan berdasarkan tracking ID.

Data penting:

```text
previous_y
line_a_frames
vehicle_speeds
```

Alur perhitungan:

```text
Tracking ID Detected
    ↓
Read Current Y Position
    ↓
Compare with Previous Y
    ↓
Crossed Line A?
    ↓
Save Frame A
    ↓
Crossed Line B?
    ↓
Calculate Frame Difference
    ↓
Calculate Travel Time
    ↓
Calculate Speed
    ↓
Save Vehicle Speed
```

Rumus waktu:

```text
travel_time_seconds = frame_difference / fps
```

Rumus kecepatan:

```text
speed_mps = distance_meters / travel_time_seconds

speed_kmh = speed_mps × 3.6
```

Nilai kecepatan masih berupa estimasi karena jarak nyata antara Line A dan Line B harus dikalibrasi berdasarkan kondisi lapangan.

---

## `line_counter.py`

Bertanggung jawab menentukan dan menggambar counting zone serta garis awal pengukuran speed.

Tugas:

- menentukan posisi garis hitung,
- menentukan batas atas dan bawah counting zone,
- menentukan posisi Speed Line A,
- menggambar counting zone,
- menggambar Speed Line A.

Visualisasi:

```text
Speed Line A
────────────────────────

Counting Zone Upper Boundary
────────────────────────

Main Counting Line / Line B
════════════════════════

Counting Zone Lower Boundary
────────────────────────
```

Counting zone menggunakan toleransi agar kendaraan tidak harus menyentuh satu koordinat piksel secara tepat.

---

## `processing.py`

Bertanggung jawab terhadap logika analisis lalu lintas.

Tugas:

- menghitung total kendaraan,
- menghitung volume,
- membaca capacity,
- menghitung VC Ratio,
- menentukan status lalu lintas.

Alur:

```text
Vehicle Count
    ↓
Total Vehicle
    ↓
Traffic Volume
    ↓
VC Ratio
    ↓
Traffic Status
```

Modul ini tidak melakukan deteksi, tracking, maupun drawing.

---

## `layout.py`

Menyimpan seluruh konfigurasi tampilan dashboard.

Contoh:

- ukuran dashboard,
- ukuran video,
- posisi panel,
- warna,
- font,
- ketebalan garis,
- posisi informasi sistem.

Tujuannya agar angka koordinat dan konfigurasi tampilan tidak ditulis berulang pada banyak file.

---

## `draw.py`

Bertanggung jawab menggambar seluruh tampilan dashboard.

Tugas:

- membuat canvas dashboard,
- menempelkan video,
- menggambar header,
- menggambar informasi sistem,
- menggambar ringkasan vehicle count,
- menggambar traffic analysis,
- menggambar footer.

Prinsip:

```text
draw.py hanya menampilkan data
draw.py tidak menghitung data
```

---

## `utils.py`

Berisi fungsi bantu yang digunakan oleh beberapa modul.

Contoh:

- mencari posisi tengah teks,
- resize frame,
- konversi atau normalisasi frame,
- fungsi umum yang tidak menjadi tanggung jawab modul tertentu.

---

## `csv_logger.py`

Bertanggung jawab menyimpan data lalu lintas ke file CSV.

Output:

```text
output/traffic_log.csv
```

Data disimpan secara periodik.

Struktur data:

```text
timestamp,motor,mobil,bus,truk,ambulans,total,capacity,vc_ratio,status
```

Pada tahap berikutnya data speed dapat ditambahkan sesuai desain penyimpanan yang disepakati.

---

## `database_logger.py`

Bertanggung jawab menyimpan data lalu lintas ke SQLite.

Output:

```text
output/traffic_data.db
```

Tabel utama:

```text
traffic_logs
```

Data yang disimpan saat ini sama dengan data CSV.

Modul ini dapat dikembangkan untuk menyimpan:

- rata-rata kecepatan,
- kecepatan per kendaraan,
- identitas kamera,
- lokasi,
- waktu pengamatan.

---

# 5. Aliran Data Antar-Modul

```text
main.py
   │
   ├── membaca frame dari OpenCV
   │
   ▼
tracker.py
   │
   ├── menjalankan YOLOv8 dan ByteTrack
   │
   ▼
result.boxes
   │
   ├──────────────► yolo_detector.py
   │                 menggambar bounding box
   │
   ├──────────────► vehicle_tracker.py
   │                 menghitung kendaraan
   │                       │
   │                       ▼
   │                 vehicle_data
   │
   └──────────────► speed_estimator.py
                     menghitung estimasi speed
                           │
                           ▼
                      speed_data

vehicle_data
     │
     ▼
processing.py
     │
     ▼
traffic_data
     │
     ├──────────────► draw.py
     ├──────────────► csv_logger.py
     └──────────────► database_logger.py
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Dashboard        CSV        SQLite
```

---

# 6. Aliran Data Dalam Satu Frame

Misalnya satu frame berisi satu mobil.

```text
Frame
  │
  ▼
YOLO mendeteksi car
  │
  ▼
ByteTrack memberi ID #12
  │
  ├──────────────► VehicleTracker
  │                 menerima:
  │                 - class = car
  │                 - ID = 12
  │                 - posisi kendaraan
  │
  │                 Class Voting:
  │                 car → mobil
  │
  │                 Mobil memasuki counting zone
  │
  │                 ID #12 belum dihitung
  │
  │                 vehicle_count["mobil"] += 1
  │
  └──────────────► SpeedEstimator
                    membaca posisi ID #12
                    │
                    ├── melewati Line A
                    │     simpan frame A
                    │
                    └── melewati Line B
                          hitung waktu
                          hitung km/jam
  │
  ▼
processing.py menghitung:
- total
- volume
- VC Ratio
- status
  │
  ▼
Data ditampilkan dan disimpan
```

---

# 7. Prinsip Arsitektur

## Separation of Concerns

Setiap modul memiliki satu fokus utama.

```text
YOLO Detector     → Deteksi dan pemetaan kelas
Tracker           → Tracking ID
VehicleTracker    → Counting
SpeedEstimator    → Estimasi kecepatan
Processing        → Analisis lalu lintas
Draw              → Tampilan
CSV Logger        → Penyimpanan CSV
Database Logger   → Penyimpanan database
```

---

## Single Responsibility

Satu class atau fungsi memiliki satu tugas utama.

Contoh:

```text
VehicleTracker
```

hanya bertanggung jawab terhadap penghitungan kendaraan.

```text
SpeedEstimator
```

hanya bertanggung jawab terhadap estimasi kecepatan.

```text
CSVLogger
```

hanya bertanggung jawab terhadap penyimpanan CSV.

```text
DatabaseLogger
```

hanya bertanggung jawab terhadap penyimpanan database.

---

## Loose Coupling

`VehicleTracker` dan `SpeedEstimator` tidak saling bergantung.

Keduanya hanya membaca input yang sama:

```text
result.boxes
```

Keuntungan:

- error speed tidak merusak counting,
- perubahan counting tidak otomatis mengubah speed,
- setiap modul dapat diuji secara terpisah,
- pengembangan fitur menjadi lebih aman.

---

## Modular Development

Fitur baru ditambahkan sebagai modul terpisah selama memiliki tanggung jawab yang berbeda.

Contoh:

```text
speed_estimator.py
```

dibuat terpisah dari:

```text
vehicle_tracker.py
```

Pendekatan ini terbukti berhasil karena Speed Estimation dapat ditambahkan tanpa menghentikan:

- Vehicle Counting,
- CSV Logger,
- SQLite Logger,
- Dashboard.

---

# 8. Implementasi Speed Estimation

Status:

```text
✅ Implemented
```

Modul:

```text
src/speed_estimator.py
```

Input:

- Tracking result
- Tracking ID
- Posisi kendaraan
- Frame number
- FPS
- Jarak antar-garis

Output:

- Estimasi kecepatan kendaraan dalam km/jam
- Data speed berdasarkan Tracking ID

Contoh output terminal:

```text
SPEED LINE A: mobil ID #44 Frame 127

KECEPATAN ESTIMASI:
mobil ID #44
26.5 km/jam
```

Keunggulan desain:

- independen dari `VehicleTracker`,
- tidak memengaruhi Vehicle Counting,
- mudah dikembangkan untuk Speed Overlay,
- mudah dikembangkan untuk Average Speed,
- dapat disimpan ke CSV dan database pada tahap berikutnya.

Batasan saat ini:

- jarak 10 meter masih berupa asumsi,
- tracking ID dapat terputus,
- kamera belum dikalibrasi,
- perubahan perspektif kamera belum dikompensasi.

---

# 9. Rencana Deployment Server

```text
GitHub Repository
       │
       ▼
Clone ke Server
       │
       ▼
Install Python
       │
       ▼
Install Requirements
       │
       ▼
Siapkan Model YOLO
       │
       ▼
Siapkan Video atau CCTV
       │
       ▼
Konfigurasi Path dan Environment
       │
       ▼
Run main.py
       │
       ▼
Testing
```

Persiapan deployment mencakup:

- versi Python,
- dependency,
- model YOLO,
- akses video,
- akses kamera,
- permission folder,
- kebutuhan GPU atau CPU,
- log aplikasi,
- konfigurasi database.

---

# 10. Roadmap Arsitektur Berikutnya

```text
Current Architecture
        │
        ▼
✅ Speed Estimation
        │
        ▼
Speed Overlay
        │
        ▼
Average Speed Dashboard
        │
        ▼
Speed Data Logging
        │
        ▼
Server Deployment
        │
        ▼
Live CCTV / RTSP
        │
        ▼
Database Online
        │
        ▼
Web Dashboard
        │
        ▼
Multi Camera Monitoring
```

---

# 11. Kesimpulan

Project telah berkembang menjadi sistem modular yang terdiri dari:

- Computer Vision,
- Object Detection,
- Multi Object Tracking,
- Vehicle Counting,
- Speed Estimation,
- Traffic Analysis,
- Dashboard Monitoring,
- CSV Logging,
- SQLite Database,
- Git Version Control,
- Project Documentation.

Arsitektur saat ini sudah mendukung pengembangan fitur lanjutan tanpa harus menulis ulang seluruh aplikasi.

Fokus pengembangan berikutnya:

- Speed Overlay,
- Average Speed Dashboard,
- Speed Data Logging,
- Server Deployment,
- Live CCTV,
- Database Online,
- Web Dashboard.

---

# 12. Versi Arsitektur

```text
Version 0.8
```

Milestone utama:

- YOLOv8 Detection
- ByteTrack Tracking
- Vehicle Counting
- VC Ratio
- Dashboard Monitoring
- CSV Logger
- SQLite Database
- Speed Estimation