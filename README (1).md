# ✋ Hand Gesture Recognition

Real-time hand gesture recognition using **MediaPipe** + **OpenCV** that maps 8 gestures to system actions including media controls, brightness, screenshot, and more.

---

## 📦 Project Structure

```
hand_gesture_recognition/
├── gesture_recognition.py   # Main webcam demo script (run this)
├── gesture_classifier.py    # Rule-based landmark classifier (8 gestures)
├── action_mapper.py         # Gesture → action + key/system simulation
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** If you face issues with mediapipe, make sure you have version 0.10.30 or above:
> ```bash
> pip install mediapipe==0.10.32
> ```

### 2. Run the demo
```bash
python gesture_recognition.py
```

On **first run**, the script will automatically download the MediaPipe hand landmarker model (~5MB) called `hand_landmarker.task`. Just wait a few seconds.

---

## 🎮 Complete Gesture → Action Mapping (8 Gestures)

| # | Gesture | How To Do It | Action | Key / Method |
|---|---------|-------------|--------|-------------|
| 1 | 👍 Thumbs Up | Only thumb up, all fingers curled | Play / Pause | Space Bar |
| 2 | ✊ Fist | All fingers AND thumb curled tightly | Previous Track | ← Left Arrow |
| 3 | 🖐️ Open Palm | All 5 fingers spread wide open | Volume Up | Volume Up Key |
| 4 | ✌️ Peace Sign | Index + middle fingers up, rest down | Next Track | → Right Arrow |
| 5 | ☝️ Pointing Up | Only index finger pointing up | Brightness Up | WMI / PowerShell |
| 6 | 🤘 Rock Sign | Index + pinky up, middle + ring down | Refresh (F5) | F5 Key |
| 7 | 🤟 Love Sign | Thumb + index + pinky up, middle + ring down | Screenshot | Saved to Pictures folder |
| 8 | 🤙 Hang Loose | Thumb + pinky out, all other fingers curled | Mute / Unmute | Volume Mute Key |

---

## 💡 Tips for Best Detection

- Keep your hand **clearly visible** in the camera frame
- Make sure you have **good lighting** — avoid dim rooms
- Hold each gesture **steady for 1–2 seconds** for it to register
- Keep your hand **30–60 cm** from the camera
- The detected gesture and action appear at the **bottom of the screen**

---

## 🖥️ Keyboard Controls

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `s` | Toggle action simulation ON / OFF |
| `h` | Toggle gesture guide panel on screen |

---

## 🧠 How It Works

### 1. MediaPipe Hand Landmarker (New Tasks API)
Uses `mediapipe.tasks.python.vision.HandLandmarker` (compatible with mediapipe 0.10.30+) to detect **21 hand landmarks** per hand in real time from webcam input.

### 2. GestureClassifier (`gesture_classifier.py`)
Uses **rule-based logic** on the relative Y-positions of fingertip vs knuckle landmarks to determine which fingers are extended:

| Landmark Role | Index |
|---|---|
| Finger Tips (index, middle, ring, pinky) | 8, 12, 16, 20 |
| Finger PIPs / knuckles | 6, 10, 14, 18 |
| Thumb Tip | 4 |
| Thumb IP | 3 |

A finger is considered **"up"** when its tip Y-coordinate is above its PIP knuckle.
Thumb detection also checks horizontal extension from the palm center.

### 3. ActionMapper (`action_mapper.py`)
Maps each gesture to a system action with **platform-specific implementations**:

- **Windows:** Uses `pyautogui` for keypresses, `wmi` library for brightness control, and `pyautogui.screenshot()` for screenshot (saved to Pictures folder with timestamp)
- **macOS:** Uses `pyautogui` or AppleScript fallback
- **Linux:** Uses `pyautogui` or `xdotool` fallback

**Cooldown system** prevents repeated triggers — each gesture has a 20-frame cooldown before it can trigger again.

### 4. Screenshot Behavior (🤟 Love Sign)
Screenshots are saved directly to your **Pictures folder** using Python (not a keyboard shortcut), so they work even when the camera window is in focus. Filename format: `gesture_screenshot_<timestamp>.png`

### 5. Brightness Behavior (☝️ Pointing Up)
On **Windows**, brightness is increased by +10% using the WMI interface (`pip install wmi`). Falls back to PowerShell if WMI is unavailable.
> Note: Brightness control only works on **laptop screens** or monitors that support software brightness control. External monitors need manual adjustment.

---

## ⚙️ Requirements

- Python 3.8+ (tested on Python 3.13)
- Webcam
- mediapipe >= 0.10.30
- opencv-python >= 4.8.0
- pyautogui >= 0.9.54

### Optional
- `wmi` — for brightness control on Windows (`pip install wmi`)
- For **Linux** without pyautogui: install `xdotool` → `sudo apt install xdotool`
- For **macOS** key simulation: grant Accessibility permission in System Preferences

---

## 🔧 Troubleshooting

| Problem | Fix |
|---------|-----|
| `module 'mediapipe' has no attribute 'solutions'` | Run `pip install mediapipe==0.10.32` |
| `ModuleNotFoundError: mediapipe.framework` | Use the latest `gesture_recognition.py` which uses Tasks API |
| Camera not opening | Make sure no other app (Zoom, Teams) is using your webcam |
| Screenshot not working | Make sure `pyautogui` is installed: `pip install pyautogui` |
| Brightness not changing | Run `pip install wmi` (Windows only, laptop screens only) |
| Gestures not detected | Improve lighting and hold gesture steady for 1–2 seconds |

---
