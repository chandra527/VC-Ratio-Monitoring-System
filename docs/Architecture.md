# VC Ratio Monitoring System

## System Architecture

Dokumen ini menjelaskan struktur aplikasi, hubungan antar-modul, serta aliran data pada project **VC Ratio Monitoring System**.

---

# 1. Tujuan Arsitektur

Arsitektur project dibuat modular agar:

- setiap bagian mempunyai tanggung jawab yang jelas,
- proses debugging lebih mudah,
- fitur baru dapat ditambahkan tanpa merusak fitur lama,
- kode lebih mudah dibaca dan dipelihara,
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
    ▼
Vehicle Tracker
    │
    ├── Vehicle Counting
    ├── Class Voting
    └── Duplicate Prevention
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
│   ├── csv_logger.py
│   └── database_logger.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

# 4. Tanggung Jawab Setiap Modul

## `main.py`

Berfungsi sebagai pusat alur aplikasi.

Tugas utama:

- membuka video,
- membaca frame,
- memanggil YOLO dan tracker,
- memperbarui vehicle count,
- menghitung data lalu lintas,
- menggambar dashboard,
- menyimpan data ke CSV,
- menyimpan data ke database,
- menampilkan aplikasi.

Alur utama:

```text
Read Frame
    ↓
Track Vehicle
    ↓
Update Vehicle Count
    ↓
Update Traffic Data
    ↓
Save CSV and Database
    ↓
Draw Dashboard
    ↓
Display
```

---

## `yolo_detector.py`

Bertanggung jawab terhadap proses deteksi kendaraan.

Tugas:

- memuat model YOLOv8,
- membaca nama kelas YOLO,
- memetakan kelas YOLO ke nama kendaraan,
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

---

## `vehicle_tracker.py`

Berfungsi sebagai memori kendaraan.

Tugas utama:

- menyimpan tracking ID,
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
Class Voting
    ↓
Seen Above Counting Zone?
    ↓
Entered Counting Zone?
    ↓
Already Counted?
    ↓
Counter +1
```

---

## `line_counter.py`

Bertanggung jawab menentukan dan menggambar counting zone.

Tugas:

- menentukan posisi garis hitung,
- menentukan batas atas dan bawah zona,
- menggambar counting zone pada frame.

Counting zone menggunakan toleransi agar kendaraan tidak harus menyentuh satu koordinat piksel secara tepat.

```text
Upper Zone Boundary
────────────────────────

Main Counting Line
════════════════════════

Lower Zone Boundary
────────────────────────
```

---

## `processing.py`

Bertanggung jawab terhadap logika analisis lalu lintas.

Tugas:

- menghitung total kendaraan,
- menghitung volume,
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

Tujuannya agar koordinat tampilan tidak ditulis berulang pada banyak file.

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

Modul ini hanya menampilkan data dan tidak menghitung data.

---

## `utils.py`

Berisi fungsi bantu yang digunakan oleh beberapa modul.

Contoh:

- mencari posisi tengah teks,
- resize frame,
- konversi frame jika diperlukan.

---

## `csv_logger.py`

Bertanggung jawab menyimpan data lalu lintas ke file CSV.

Output:

```text
output/traffic_log.csv
```

Data disimpan secara periodik.

Contoh struktur data:

```text
timestamp,motor,mobil,bus,truk,ambulans,total,capacity,vc_ratio,status
```

---

## `database_logger.py`

Bertanggung jawab menyimpan data ke SQLite.

Output:

```text
output/traffic_data.db
```

Tabel utama:

```text
traffic_logs
```

Data yang disimpan sama dengan data CSV.

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
   ├── menjalankan ByteTrack
   │
   ▼
result.boxes
   │
   ├──────────────► yolo_detector.py
   │                 menggambar bounding box
   │
   └──────────────► vehicle_tracker.py
                     menghitung kendaraan
                          │
                          ▼
                    vehicle_data
                          │
                          ▼
                    processing.py
                          │
                          ▼
                    traffic_data
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
         draw.py      csv_logger.py  database_logger.py
            │             │             │
            ▼             ▼             ▼
        Dashboard         CSV         SQLite
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
  ▼
VehicleTracker menerima:
- class = car
- ID = 12
- posisi kendaraan
  │
  ▼
Class Voting:
car → mobil
  │
  ▼
Mobil memasuki counting zone
  │
  ▼
ID #12 belum pernah dihitung
  │
  ▼
vehicle_count["mobil"] += 1
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
YOLO Detector    → Deteksi
Tracker          → Tracking ID
VehicleTracker   → Counting
Processing       → Analisis
Draw             → Tampilan
CSV Logger       → Penyimpanan CSV
Database Logger  → Penyimpanan database
```

---

## Single Responsibility

Satu class atau fungsi sebaiknya memiliki satu tugas utama.

Contoh:

```text
CSVLogger
```

hanya bertugas menyimpan CSV.

```text
DatabaseLogger
```

hanya bertugas menyimpan data ke database.

---

## Modular Development

Fitur baru ditambahkan sebagai modul terpisah.

Contoh roadmap berikutnya:

```text
speed_estimator.py
```

Modul kecepatan akan dibuat terpisah agar tidak merusak `VehicleTracker`.

---

# 8. Rencana Speed Estimation

Speed estimation akan menggunakan arsitektur:

```text
Tracking Result
      │
      ├────────────► VehicleTracker
      │               menghitung kendaraan
      │
      └────────────► SpeedEstimator
                      menghitung kecepatan
```

Dengan pemisahan ini:

- counting tetap stabil,
- speed dapat diuji sendiri,
- error speed tidak memengaruhi jumlah kendaraan,
- kode lebih mudah dirawat.

Rencana file:

```text
src/speed_estimator.py
```

Data yang akan disimpan:

```text
line_a_frames
line_b_frames
vehicle_speeds
```

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
Run main.py
```

---

# 10. Roadmap Arsitektur Berikutnya

```text
Current Architecture
        │
        ▼
Speed Estimator
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

Project telah dikembangkan menjadi sistem modular yang terdiri dari:

- Computer Vision,
- Object Tracking,
- Vehicle Counting,
- Traffic Analysis,
- Dashboard Monitoring,
- CSV Logging,
- SQLite Database,
- Git Version Control.

Arsitektur ini menjadi dasar untuk fitur berikutnya, terutama:

- Speed Estimation,
- Server Deployment,
- Live CCTV,
- Database Online,
- Web Dashboard.