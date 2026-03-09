# ✋ Hand Gesture Recognition
### Syntecxhub AI Internship — Task 3, Project 2

Real-time hand gesture recognition using **MediaPipe** + **OpenCV** that maps gestures to media-control actions.

---

## 📦 Project Structure

```
hand_gesture_recognition/
├── gesture_recognition.py   # Main webcam demo script
├── gesture_classifier.py    # Rule-based landmark classifier
├── action_mapper.py         # Gesture → action + key simulation
├── requirements.txt
└── README.md
```

---

## 🚀 Setup & Run

### 1. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the demo
```bash
python gesture_recognition.py
```

---

## 🎮 Gesture → Action Mapping

| Gesture       | Action            | Simulated Key |
|---------------|-------------------|---------------|
| ✌️ Peace Sign  | Next Track        | → Right Arrow |
| ✊ Fist         | Previous Track    | ← Left Arrow  |
| 👍 Thumbs Up   | Play / Pause      | Space Bar     |
| 🖐️ Open Palm   | Volume Up         | ↑ Up Arrow    |

---

## 🖥️ Controls

| Key | Action                              |
|-----|-------------------------------------|
| `q` | Quit the application                |
| `s` | Toggle action simulation ON / OFF   |

---

## 🧠 How It Works

1. **MediaPipe Hands** detects 21 hand landmarks per hand in real time.
2. **GestureClassifier** analyses relative positions of fingertip and knuckle landmarks using rule-based logic to classify gestures.
3. **ActionMapper** maps each gesture to a media action and simulates the corresponding keypress (cross-platform: Windows / macOS / Linux).
4. **Cooldown system** prevents repeated triggers from a held gesture.

### Landmark-based Rules

| Gesture    | Rule                                                           |
|------------|----------------------------------------------------------------|
| Open Palm  | Thumb up + all 4 fingers extended                             |
| Fist       | Thumb down + all 4 fingers curled                             |
| Thumbs Up  | Thumb up + all 4 fingers curled                               |
| Peace Sign | Index + middle up, ring + pinky curled                        |

---

## ⚙️ Requirements

- Python 3.8+
- Webcam
- `opencv-python`, `mediapipe`, `pyautogui` (optional, for key simulation)

---

## 📝 Notes

- For **Linux** key simulation without `pyautogui`, install `xdotool`: `sudo apt install xdotool`
- For **macOS**, System Events permission must be granted in System Preferences → Security & Privacy → Accessibility.
- Works with **up to 2 hands** simultaneously (actions triggered from first detected hand).

---

## 👨‍💻 Author
Syntecxhub AI Internship Program
