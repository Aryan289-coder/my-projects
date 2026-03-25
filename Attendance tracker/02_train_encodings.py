"""
STEP 2 — Train Face Encodings
================================
Run this script ONCE after collecting photos for ALL students.
It reads all photos from the dataset/ folder and generates
face encodings, saved to encodings.pkl

Usage:
    python 02_train_encodings.py

Re-run this whenever you add new students.
"""

import face_recognition
import os
import pickle
import cv2
import sys

def train_encodings():
    print("=" * 50)
    print("   TRAINING FACE ENCODINGS")
    print("=" * 50)

    dataset_path = "dataset"

    if not os.path.exists(dataset_path):
        print("❌ 'dataset' folder not found!")
        print("   Please run 01_collect_photos.py first.")
        sys.exit(1)

    student_folders = [
        f for f in os.listdir(dataset_path)
        if os.path.isdir(os.path.join(dataset_path, f))
    ]

    if not student_folders:
        print("❌ No student folders found in dataset/")
        print("   Please run 01_collect_photos.py first.")
        sys.exit(1)

    print(f"\n📁 Found {len(student_folders)} student(s): {', '.join(student_folders)}\n")

    known_encodings = []
    known_names = []
    failed = []

    for student in student_folders:
        student_dir = os.path.join(dataset_path, student)
        images = [
            f for f in os.listdir(student_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        if not images:
            print(f"   ⚠ No images found for {student}, skipping.")
            continue

        print(f"   🔍 Processing: {student} ({len(images)} photos)...")
        success_count = 0

        for img_file in images:
            img_path = os.path.join(student_dir, img_file)

            # Load with OpenCV and convert to proper RGB (fixes RGBA/grayscale issues)
            bgr = cv2.imread(img_path)
            if bgr is None:
                print(f"      ⚠ Could not read {img_file}, skipping.")
                failed.append(img_path)
                continue

            # Convert BGR → RGB (face_recognition needs RGB, not BGR or RGBA)
            img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

            encs = face_recognition.face_encodings(img)

            if len(encs) > 0:
                known_encodings.append(encs[0])
                known_names.append(student.replace("_", " "))  # convert back to readable name
                success_count += 1
            else:
                failed.append(img_path)

        print(f"      ✅ Encoded {success_count}/{len(images)} photos successfully")

    if not known_encodings:
        print("\n❌ No valid face encodings found. Make sure photos have clear faces.")
        sys.exit(1)

    # Save encodings
    data = {"encodings": known_encodings, "names": known_names}
    with open("encodings.pkl", "wb") as f:
        pickle.dump(data, f)

    print(f"\n{'=' * 50}")
    print(f"✅ Training complete!")
    print(f"   Total encodings saved : {len(known_encodings)}")
    print(f"   Students registered   : {len(set(known_names))}")
    print(f"   Saved to              : encodings.pkl")

    if failed:
        print(f"\n⚠ {len(failed)} image(s) had no detectable face:")
        for f in failed:
            print(f"   - {f}")

    print(f"\nNow run: python 03_take_attendance.py")


if __name__ == "__main__":
    train_encodings()
