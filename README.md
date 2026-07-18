# 🚦 VC Ratio Monitoring System

Realtime Traffic Monitoring System menggunakan **YOLOv8**, **OpenCV**, dan **Python** untuk mendeteksi kendaraan, menghitung volume lalu lintas, VC Ratio, serta mengestimasi kecepatan kendaraan dari rekaman CCTV.

---

# 📖 About Project

Project ini dikembangkan sebagai media pembelajaran Computer Vision sekaligus prototype sistem monitoring lalu lintas yang dipersiapkan menuju implementasi pada lingkungan Dishub.

Project dibangun secara modular sehingga setiap fitur dapat dikembangkan tanpa mengganggu modul lainnya.

---

# 🎯 Tujuan Project

- Deteksi kendaraan secara realtime
- Multi Object Tracking menggunakan ByteTrack
- Vehicle Counting berdasarkan Tracking ID
- Menghitung Volume Kendaraan
- Menghitung VC Ratio
- Estimasi Kecepatan Kendaraan
- Menampilkan Dashboard Monitoring
- Menyimpan data ke CSV
- Menyimpan data ke SQLite Database

---

# 📸 Dashboard

> *(Screenshot dashboard akan ditambahkan setelah tampilan final selesai.)*

---

# ✨ Features

## Computer Vision

- ✅ OpenCV Video Streaming
- ✅ YOLOv8 Vehicle Detection
- ✅ Bounding Box
- ✅ Vehicle Label
- ✅ ByteTrack Multi Object Tracking

---

## Traffic Analysis

- ✅ Vehicle Counting
- ✅ Vehicle Classification Voting
- ✅ Traffic Volume
- ✅ Capacity
- ✅ VC Ratio
- ✅ Traffic Status
- ✅ Speed Estimation

---

## Data Logging

- ✅ CSV Logger
- ✅ SQLite Database Logger

---

## Dashboard

- ✅ Professional Dashboard
- ✅ Camera View
- ✅ Vehicle Count Panel
- ✅ Traffic Analysis Panel
- ✅ System Information

---

## Software Engineering

- ✅ Modular Architecture
- ✅ Refactoring
- ✅ Git Version Control
- ✅ GitHub Repository
- ✅ Project Documentation

---

# 📂 Project Structure

```text
VC_RATIO_PROJECT_NEW
│
├── data/
│
├── docs/
│   ├── Progress_Report.md
│   └── Architecture.md
│
├── models/
│
├── output/
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
├── requirements.txt
└── README.md
```

---

# 🛠 Technologies

- Python
- OpenCV
- YOLOv8 (Ultralytics)
- ByteTrack
- SQLite
- CSV
- NumPy
- Git
- GitHub

---

# 🚀 Installation

Clone repository

```bash
git clone https://github.com/chandra527/VC-Ratio-Monitoring-System.git
```

Masuk ke folder project

```bash
cd VC-Ratio-Monitoring-System
```

Install dependency

```bash
pip install -r requirements.txt
```

Jalankan aplikasi

```bash
python src/main.py
```

---

# 📈 Development Roadmap

## ✅ Completed

- OpenCV Streaming
- Dashboard
- YOLOv8 Detection
- ByteTrack Tracking
- Vehicle Counting
- Traffic Volume
- VC Ratio
- CSV Logger
- SQLite Database
- Speed Estimation

---

## 🚧 Next Development

- Speed Overlay
- Average Speed Dashboard
- Vehicle Log
- Live CCTV (RTSP)
- Server Deployment
- Database Online
- Web Dashboard

---

# 📚 Documentation

Project documentation tersedia pada folder:

```text
docs/
```

- Progress_Report.md
- Architecture.md

---

# 👨‍💻 Developer

**Eggi Chandra**

Bachelor of Informatics Engineering

Indonesia

---

# ⭐ Current Version

**Version 0.8**

Milestone:

- Vehicle Detection
- Tracking
- Vehicle Counting
- VC Ratio
- CSV Logger
- SQLite Database
- Speed Estimation


## Features

- Vehicle Detection (YOLOv8)
- Multi Object Tracking (ByteTrack)
- Vehicle Counting
- Speed Estimation
- VC Ratio Calculation
- Traffic Status Classification
- CSV Logging
- MySQL Database Logging

