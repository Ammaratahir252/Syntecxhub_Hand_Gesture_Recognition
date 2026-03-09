"""
Hand Gesture Recognition System
Syntecxhub Internship - Task 3, Project 2
Compatible with mediapipe 0.10.30+, Python 3.13

Gestures & Actions:
  👍 Thumbs Up   → Play / Pause
  ✊ Fist         → Previous Track
  🖐️ Open Palm   → Volume Up
  ✌️ Peace Sign   → Next Track
  ☝️ Pointing Up  → Brightness Up
  🤘 Rock Sign    → Brightness Up
  🤟 Love Sign    → Brightness Up
  🤙 Hang Loose   → Mute / Unmute
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import time
import urllib.request
import os

from gesture_classifier import GestureClassifier
from action_mapper import ActionMapper

# ─── Download model if not present ───────────────────────────────────────────
MODEL_PATH = "hand_landmarker.task"
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("[INFO] Downloading hand landmarker model (~5MB)...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("[INFO] Model downloaded.")

# ─── Colour palette ───────────────────────────────────────────────────────────
COLORS = {
    "Thumbs Up":   (0,   200,  80),
    "Fist":        (0,    80, 220),
    "Open Palm":   (0,   180, 220),
    "Peace Sign":  (200,  80, 220),
    "Pointing Up": (255, 200,   0),
    "Rock Sign":   (255, 100,   0),
    "Love Sign":   (255,  50, 150),
    "Hang Loose":  (0,   230, 180),
    "Unknown":     (120, 120, 120),
}

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17),
]

# Gesture hint reference shown on screen
GESTURE_HINTS = [
    "Thumbs Up  = Play/Pause",
    "Fist       = Previous",
    "Open Palm  = Vol Up",
    "Peace Sign = Next",
    "Pointing Up= Brightness",
    "Rock Sign  = Refresh (F5)",
    "Love Sign  = Screenshot",
    "Hang Loose = Mute",
]


def draw_landmarks(frame, hand_landmarks_list, gesture):
    h, w = frame.shape[:2]
    color = COLORS.get(gesture, COLORS["Unknown"])
    for hand_lms in hand_landmarks_list:
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_lms]
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], color, 2)
        for i, pt in enumerate(pts):
            dot_color = (255, 255, 255) if i not in [4,8,12,16,20] else color
            cv2.circle(frame, pt, 5, dot_color, -1)
            cv2.circle(frame, pt, 5, (0, 0, 0), 1)


def draw_hint_panel(frame, show_hints):
    if not show_hints:
        h, w = frame.shape[:2]
        cv2.putText(frame, "Press 'h' for gesture guide",
                    (w - 310, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150,150,150), 1)
        return

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 65), (310, 65 + len(GESTURE_HINTS) * 22 + 10),
                  (20, 20, 40), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    for i, hint in enumerate(GESTURE_HINTS):
        cv2.putText(frame, hint, (8, 85 + i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1)


def draw_ui(frame, gesture, action, fps, simulate):
    h, w = frame.shape[:2]

    # Top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 60), (20, 20, 40), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 2)
    sim_col = (0, 220, 100) if simulate else (80, 80, 80)
    cv2.putText(frame, f"Actions: {'ON' if simulate else 'OFF'} [s]",
                (w - 230, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, sim_col, 2)

    # Bottom bar
    color = COLORS.get(gesture, COLORS["Unknown"])
    cv2.rectangle(frame, (0, h - 90), (w, h), (15, 15, 30), -1)
    cv2.putText(frame, f"Gesture: {gesture}", (15, h - 55),
                cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 2)
    cv2.putText(frame, f"Action : {action}", (15, h - 18),
                cv2.FONT_HERSHEY_DUPLEX, 0.75, (220, 220, 220), 2)
    return frame


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  720)

    classifier  = GestureClassifier()
    mapper      = ActionMapper()

    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options      = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    detector = vision.HandLandmarker.create_from_options(options)

    prev_time    = time.time()
    simulate     = True
    show_hints   = True
    last_gesture = "Unknown"
    last_action  = "—"
    cooldown     = 0

    print("\n╔══════════════════════════════════════════╗")
    print("║   Hand Gesture Recognition — Syntecxhub ║")
    print("╠══════════════════════════════════════════╣")
    print("║  q = Quit  |  s = Toggle Actions         ║")
    print("║  h = Toggle gesture guide on screen      ║")
    print("╚══════════════════════════════════════════╝\n")
    print("Gestures:")
    for hint in GESTURE_HINTS:
        print(f"  {hint}")
    print()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame     = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result    = detector.detect(mp_image)

        detected_gestures = []

        if result.hand_landmarks:
            for hand_lms in result.hand_landmarks:
                gesture = classifier.classify_new(hand_lms)
                detected_gestures.append(gesture)

            draw_landmarks(frame, result.hand_landmarks,
                           detected_gestures[0] if detected_gestures else "Unknown")

            for i, (hand_lms, gesture) in enumerate(
                    zip(result.hand_landmarks, detected_gestures)):
                wrist = hand_lms[0]
                cx = int(wrist.x * frame.shape[1])
                cy = int(wrist.y * frame.shape[0]) - 25
                color = COLORS.get(gesture, COLORS["Unknown"])
                cv2.putText(frame, gesture, (cx - 60, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        current_gesture = detected_gestures[0] if detected_gestures else "Unknown"

        if current_gesture != last_gesture or cooldown == 0:
            action = mapper.get_action(current_gesture)
            if simulate and current_gesture != "Unknown":
                mapper.simulate(current_gesture)
            last_gesture = current_gesture
            last_action  = action
            cooldown     = 20
        else:
            cooldown = max(0, cooldown - 1)

        now       = time.time()
        fps       = 1.0 / (now - prev_time + 1e-6)
        prev_time = now

        draw_hint_panel(frame, show_hints)
        frame = draw_ui(frame, last_gesture, last_action, fps, simulate)
        cv2.imshow("Hand Gesture Recognition — Syntecxhub", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            simulate = not simulate
            print(f"[INFO] Action simulation {'ON' if simulate else 'OFF'}")
        elif key == ord('h'):
            show_hints = not show_hints

    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("[INFO] Session ended.")


if __name__ == "__main__":
    main()