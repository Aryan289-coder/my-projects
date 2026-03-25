"""
STEP 1 — Collect Student Photos
================================
Run this script once for EACH student.
It will open your webcam and capture 10 photos automatically.

Usage:
    python 01_collect_photos.py
"""

import cv2
import os
import time

def collect_photos():
    print("=" * 50)
    print("   STUDENT PHOTO COLLECTION")
    print("=" * 50)

    # Get student name
    name = input("\nEnter student full name (e.g. Rahul Sharma): ").strip()
    if not name:
        print("❌ Name cannot be empty!")
        return

    # Clean name for folder (replace spaces with underscore)
    folder_name = name.replace(" ", "_")
    save_path = os.path.join("dataset", folder_name)
    os.makedirs(save_path, exist_ok=True)

    # Check how many photos already exist
    existing = len([f for f in os.listdir(save_path) if f.endswith(".jpg")])
    print(f"\n📁 Saving to: dataset/{folder_name}/")
    print(f"📷 Photos already saved: {existing}")
    print(f"\n✅ Instructions:")
    print("   - Look straight at the camera")
    print("   - Move your head slightly for variety")
    print("   - Press 'Q' to quit early\n")

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open webcam! Check your camera connection.")
        return

    # Load face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    count = existing
    target = existing + 10  # capture 10 more photos
    last_capture_time = 0
    capture_interval = 1.5  # seconds between captures

    print(f"Starting capture... Will take {target - existing} photos.")
    time.sleep(1)

    while count < target:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read from webcam.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

        display_frame = frame.copy()
        current_time = time.time()

        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Auto-capture if enough time has passed
            if current_time - last_capture_time >= capture_interval:
                count += 1
                filename = os.path.join(save_path, f"{count}.jpg")
                cv2.imwrite(filename, frame)
                last_capture_time = current_time
                print(f"   📸 Captured photo {count}/{target}")

        # UI overlay
        progress = count - existing
        total_needed = target - existing
        bar = "█" * progress + "░" * (total_needed - progress)
        cv2.putText(display_frame, f"Student: {name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Photos: {progress}/{total_needed}  [{bar}]", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.putText(display_frame, "Press Q to quit", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

        if len(faces) == 0:
            cv2.putText(display_frame, "⚠ No face detected - look at camera", (10, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("Photo Collection - Press Q to quit", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            print("\n⏹ Stopped early by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

    total_saved = len([f for f in os.listdir(save_path) if f.endswith(".jpg")])
    print(f"\n✅ Done! Total photos for {name}: {total_saved}")
    print(f"📁 Saved in: dataset/{folder_name}/")
    print("\nRun this script again for the next student.")
    print("When all students are added, run: python 02_train_encodings.py")


if __name__ == "__main__":
    collect_photos()
