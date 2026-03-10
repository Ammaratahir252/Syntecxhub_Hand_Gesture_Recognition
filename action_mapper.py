import platform
import subprocess
import time
import os

_OS = platform.system()

# Screenshot cooldown to avoid multiple rapid screenshots
_last_screenshot_time = 0
_last_brightness_time = 0


class ActionMapper:
    GESTURE_ACTION_MAP = {
        "Thumbs Up":   ("Play / Pause",    "space"),
        "Fist":        ("Previous Track",  "left"),
        "Open Palm":   ("Volume Up",       "volumeup"),
        "Peace Sign":  ("Next Track",      "right"),
        "Pointing Up": ("Brightness Up",   "brightness_up"),
        "Rock Sign":   ("Refresh",         "f5"),
        "Love Sign":   ("Screenshot",      "screenshot"),
        "Hang Loose":  ("Mute / Unmute",   "volumemute"),
        "Unknown":     ("—",               None),
    }

    def get_action(self, gesture: str) -> str:
        return self.GESTURE_ACTION_MAP.get(gesture, ("—", None))[0]

    def simulate(self, gesture: str):
        _, key = self.GESTURE_ACTION_MAP.get(gesture, ("—", None))
        if key is None:
            return
        try:
            if _OS == "Windows":
                self._windows_key(key)
            elif _OS == "Darwin":
                self._macos_key(key)
            else:
                self._linux_key(key)
            print(f"[ACTION] {gesture}  →  {self.get_action(gesture)}")
        except Exception as e:
            print(f"[WARN] Could not simulate '{key}': {e}")

    # ── Windows ───────────────────────────────────────────────────────────────
    def _windows_key(self, key: str):
        global _last_screenshot_time, _last_brightness_time

        # ── Brightness via WMI ────────────────────────────────────────────────
        if key == "brightness_up":
            now = time.time()
            if now - _last_brightness_time < 1.5:
                return
            _last_brightness_time = now
            try:
                import wmi
                c = wmi.WMI(namespace="wmi")
                methods = c.WmiMonitorBrightnessMethods()[0]
                current = c.WmiMonitorBrightness()[0].CurrentBrightness
                new_val = min(current + 10, 100)
                methods.WmiSetBrightness(new_val, 0)
                print(f"[BRIGHTNESS] {current}% → {new_val}%")
            except ImportError:
                # fallback: PowerShell
                ps = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,70)"
                subprocess.run(["powershell", "-Command", ps],
                               capture_output=True, check=False)
                print("[BRIGHTNESS] Set via PowerShell")
            except Exception as e:
                print(f"[WARN] Brightness failed: {e}")
            return

        # ── Screenshot via PIL/pyautogui ──────────────────────────────────────
        if key == "screenshot":
            now = time.time()
            if now - _last_screenshot_time < 2.0:
                return
            _last_screenshot_time = now
            try:
                import pyautogui
                pictures = os.path.join(os.path.expanduser("~"), "Pictures")
                os.makedirs(pictures, exist_ok=True)
                filename = os.path.join(pictures,
                    f"gesture_screenshot_{int(time.time())}.png")
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)
                print(f"[SCREENSHOT] Saved → {filename}")
            except Exception as e:
                print(f"[WARN] Screenshot failed: {e}")
            return

        # ── Standard keys ─────────────────────────────────────────────────────
        VK = {
            "space":      0x20,
            "left":       0x25,
            "right":      0x27,
            "f5":         0x74,
            "volumeup":   0xAF,
            "volumedown": 0xAE,
            "volumemute": 0xAD,
        }
        try:
            import pyautogui
            pg_map = {
                "space": "space", "left": "left", "right": "right",
                "f5": "f5", "volumeup": "volumeup",
                "volumedown": "volumedown", "volumemute": "volumemute",
            }
            pyautogui.press(pg_map.get(key, key))
        except ImportError:
            import ctypes
            vk = VK.get(key)
            if vk:
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
                ctypes.windll.user32.keybd_event(vk, 0, 2, 0)

    # ── macOS ─────────────────────────────────────────────────────────────────
    def _macos_key(self, key: str):
        if key == "brightness_up":
            subprocess.run(["osascript", "-e",
                'tell application "System Events" to key code 144'], check=False)
            return
        if key == "screenshot":
            pictures = os.path.join(os.path.expanduser("~"), "Pictures")
            filename = os.path.join(pictures, f"gesture_screenshot_{int(time.time())}.png")
            subprocess.run(["screencapture", filename], check=False)
            print(f"[SCREENSHOT] Saved → {filename}")
            return
        try:
            import pyautogui
            pg_map = {
                "space": "space", "left": "left", "right": "right",
                "f5": "f5", "volumeup": "volumeup",
                "volumedown": "volumedown", "volumemute": "volumemute",
            }
            pyautogui.press(pg_map.get(key, key))
        except ImportError:
            pass

    # ── Linux ─────────────────────────────────────────────────────────────────
    def _linux_key(self, key: str):
        if key == "brightness_up":
            subprocess.run(["xdotool", "key", "XF86MonBrightnessUp"], check=False)
            return
        if key == "screenshot":
            pictures = os.path.join(os.path.expanduser("~"), "Pictures")
            filename = os.path.join(pictures, f"gesture_screenshot_{int(time.time())}.png")
            subprocess.run(["scrot", filename], check=False)
            print(f"[SCREENSHOT] Saved → {filename}")
            return
        xdg = {
            "space": "space", "left": "Left", "right": "Right",
            "f5": "F5", "volumeup": "XF86AudioRaiseVolume",
            "volumedown": "XF86AudioLowerVolume", "volumemute": "XF86AudioMute",
        }
        try:
            import pyautogui
            pyautogui.press(xdg.get(key, key))
        except ImportError:
            subprocess.run(["xdotool", "key", xdg.get(key, key)], check=False)
