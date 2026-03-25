# 🎓 Face Recognition Attendance System
### Built with Python + OpenCV + face_recognition

---

## 📦 Installation

### Step 1: Install Python libraries

```bash
pip install -r requirements.txt
```

> ⚠️ **Windows users**: `face_recognition` needs `dlib` which requires CMake.
> Easier fix — install a pre-built dlib wheel:
> 1. Go to: https://github.com/z-mahmud22/Dlib_Windows_Python3.x
> 2. Download the `.whl` that matches your Python version
> 3. Run: `pip install dlib-XX-cpXX-win_amd64.whl`
> 4. Then: `pip install face_recognition`

> ✅ **Linux/Mac**: Just `pip install -r requirements.txt` should work.

---

## 🚀 How to Use (Follow These Steps in Order)

### 🔹 One-time setup (do this ONCE per project)

**1. Collect photos for each student:**
```bash
python 01_collect_photos.py
```
- Enter the student's name when prompted
- Look at the camera — it auto-captures 10 photos
- Run again for every student

**2. Train face encodings:**
```bash
python 02_train_encodings.py
```
- Run this ONCE after collecting photos for ALL students
- Creates `encodings.pkl` — re-run if you add new students

---

### 🔹 Every lecture (run these each class)

**3. Take attendance:**
```bash
python 03_take_attendance.py
```
- Enter subject name and lecture number
- Camera opens — students walk in front of it
- Recognized students auto-marked as Present
- Press **Q** to finish → CSV saved automatically

**4. View reports:**
```bash
python 04_view_report.py
```
- See full attendance table
- Per-student attendance percentage
- Export to Excel

---

## 📁 Project Structure

```
attendance_system/
├── dataset/                    ← Student photos (auto-created)
│   ├── Rahul_Sharma/
│   │   ├── 1.jpg
│   │   └── ...
│   └── Priya_Patel/
├── attendance_records/         ← CSV files per lecture (auto-created)
│   ├── Mathematics_L1_2024-01-15.csv
│   └── Physics_L2_2024-01-16.csv
├── 01_collect_photos.py
├── 02_train_encodings.py
├── 03_take_attendance.py
├── 04_view_report.py
├── encodings.pkl               ← Generated after training
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuration (in 03_take_attendance.py)

| Setting | Default | Meaning |
|---|---|---|
| `CONFIDENCE_THRESHOLD` | `0.50` | Lower = stricter match. Try 0.45–0.55 |
| `FRAME_SKIP` | `3` | Process every 3rd frame (higher = faster) |

---

## 🛠 Troubleshooting

| Problem | Fix |
|---|---|
| Camera not opening | Check `cv2.VideoCapture(0)` — try `1` if 0 fails |
| Face not detected during photo collection | Improve lighting, remove glasses temporarily |
| Wrong student recognized | Retake photos with better lighting; lower threshold |
| `dlib` install fails on Windows | Use pre-built wheel (see Installation above) |
| `encodings.pkl` not found | Run `02_train_encodings.py` first |

---

## 📊 Output CSV Format

```
Student Name, Time Detected, Status
Rahul Sharma, 09:15:42, Present
Priya Patel,  09:16:08, Present
```

Each lecture creates a separate CSV file named:
`attendance_<Subject>_<LectureNo>_<Date>.csv`
