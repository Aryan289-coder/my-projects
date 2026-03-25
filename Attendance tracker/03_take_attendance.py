"""
STEP 3 — Take Attendance (Main Script)
========================================
Run this at the START of every lecture.
Opens webcam, recognizes students in real time,
and saves attendance to a CSV file.

Usage:
    python 03_take_attendance.py

Controls:
    Q  → Quit and save attendance
    S  → Show attendance count so far
"""

import face_recognition
import cv2
import numpy as np
import pickle
import csv
import os
import sys
from datetime import datetime


# ─── CONFIG ──────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.50   # Lower = stricter matching (0.4–0.6 is good)
FRAME_SKIP = 3                 # Process every Nth frame (higher = faster but less responsive)
ATTENDANCE_FOLDER = "attendance_records"
ENCODINGS_FILE = "encodings.pkl"
# ─────────────────────────────────────────────────────────


def load_encodings():
    """Load saved face encodings from disk."""
    if not os.path.exists(ENCODINGS_FILE):
        print(f"❌ '{ENCODINGS_FILE}' not found!")
        print("   Please run 02_train_encodings.py first.")
        sys.exit(1)

    print(f"📂 Loading face encodings from {ENCODINGS_FILE}...")
    with open(ENCODINGS_FILE, "rb") as f:
        data = pickle.load(f)

    print(f"✅ Loaded {len(data['encodings'])} encodings for {len(set(data['names']))} student(s)")
    return data["encodings"], data["names"]


def get_lecture_info():
    """Ask teacher for subject and lecture details."""
    print("\n" + "=" * 55)
    print("   📋 LECTURE ATTENDANCE SYSTEM")
    print("=" * 55)

    subject = input("\nEnter subject name (e.g. Mathematics): ").strip()
    lecture_no = input("Enter lecture number (e.g. L3): ").strip()

    if not subject or not lecture_no:
        print("❌ Subject and lecture number cannot be empty!")
        sys.exit(1)

    lecture_id = f"{subject.replace(' ', '_')}_{lecture_no}"
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{lecture_id}_{date_str}.csv"

    print(f"\n📋 Lecture  : {subject} — {lecture_no}")
    print(f"📅 Date     : {date_str}")
    print(f"💾 Saving to: {ATTENDANCE_FOLDER}/{filename}")
    print(f"\n⏳ Starting camera in 2 seconds...")

    import time; time.sleep(2)
    return lecture_id, filename


def save_attendance_csv(filename, attendance_log):
    """Write attendance data to CSV file."""
    os.makedirs(ATTENDANCE_FOLDER, exist_ok=True)
    filepath = os.path.join(ATTENDANCE_FOLDER, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Student Name", "Time Detected", "Status"])
        for name, time_str in attendance_log.items():
            writer.writerow([name, time_str, "Present"])

    return filepath


def run_attendance(known_encodings, known_names, lecture_id, csv_filename):
    """Main loop: open camera, detect + recognize faces, mark attendance."""

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open webcam!")
        sys.exit(1)

    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

    print("\n🎥 Camera opened. Scanning for students...")
    print("   Press  Q  to finish and save attendance")
    print("   Press  S  to see current attendance count\n")

    attendance_log = {}   # {name: first_seen_time}
    frame_count = 0
    face_locations = []
    face_names = []

    # Colors
    COLOR_PRESENT  = (0, 220, 100)    # Green
    COLOR_UNKNOWN  = (0, 80, 220)     # Red/Orange
    COLOR_BOX      = (255, 255, 255)  # White outline

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame from webcam.")
            break

        frame_count += 1

        # ── Only process every Nth frame for speed ──
        if frame_count % FRAME_SKIP == 0:
            # Resize to 1/4 size for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Detect faces
            face_locations = face_recognition.face_locations(rgb_small, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

            face_names = []
            for face_enc in face_encodings:
                name = "Unknown"
                color = COLOR_UNKNOWN

                if known_encodings:
                    distances = face_recognition.face_distance(known_encodings, face_enc)
                    best_idx = np.argmin(distances)
                    best_distance = distances[best_idx]

                    if best_distance < CONFIDENCE_THRESHOLD:
                        name = known_names[best_idx]
                        color = COLOR_PRESENT

                        # Mark attendance if not already marked
                        if name not in attendance_log:
                            time_now = datetime.now().strftime("%H:%M:%S")
                            attendance_log[name] = time_now
                            print(f"   ✅ PRESENT: {name}  [{time_now}]")

                face_names.append((name, color))

        # ── Draw results on full-size frame ──
        display = frame.copy()
        scale = 4  # because we resized to 1/4

        for (top, right, bottom, left), (name, color) in zip(face_locations, face_names):
            top    *= scale
            right  *= scale
            bottom *= scale
            left   *= scale

            # Outer box
            cv2.rectangle(display, (left, top), (right, bottom), color, 2)

            # Label background
            label_h = 28
            cv2.rectangle(display, (left, bottom), (right, bottom + label_h), color, cv2.FILLED)
            cv2.putText(display, name, (left + 6, bottom + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)

        # ── HUD overlay ──
        h, w = display.shape[:2]

        # Top bar background
        cv2.rectangle(display, (0, 0), (w, 60), (20, 20, 20), cv2.FILLED)

        cv2.putText(display, f"Lecture: {lecture_id}", (10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display, f"Date: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}", (10, 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

        present_count = len(attendance_log)
        cv2.putText(display, f"Present: {present_count}", (w - 160, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 100), 2)
        cv2.putText(display, "Q=Quit  S=Show", (w - 185, 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

        # Show present names on right side
        y_offset = 80
        cv2.putText(display, "Marked Present:", (w - 220, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 220, 100), 1)
        for student_name, t in list(attendance_log.items())[-8:]:  # show last 8
            y_offset += 22
            cv2.putText(display, f"  {student_name} ({t})", (w - 220, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 255, 200), 1)

        cv2.imshow("Attendance System — Press Q to finish", display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == ord('Q'):
            print("\n⏹ Ending attendance session...")
            break

        if key == ord('s') or key == ord('S'):
            print(f"\n📋 Attendance so far ({present_count} students):")
            for n, t in attendance_log.items():
                print(f"   ✅ {n} — {t}")
            print()

    cap.release()
    cv2.destroyAllWindows()
    return attendance_log


def main():
    # 1. Load trained encodings
    known_encodings, known_names = load_encodings()

    # 2. Get lecture info from teacher
    lecture_id, csv_filename = get_lecture_info()

    # 3. Run live face recognition
    attendance_log = run_attendance(known_encodings, known_names, lecture_id, csv_filename)

    # 4. Save to CSV
    if attendance_log:
        filepath = save_attendance_csv(csv_filename, attendance_log)
        print(f"\n{'=' * 55}")
        print(f"✅ Attendance saved to: {filepath}")
        print(f"   Total present: {len(attendance_log)} student(s)\n")
        for name, time_str in attendance_log.items():
            print(f"   ✅ {name}  —  {time_str}")
    else:
        print("\n⚠ No students were recognized. CSV not saved.")

    print("\nDone! Run python 04_view_report.py to see full reports.")


if __name__ == "__main__":
    main()
