"""
gesture_classifier.py
─────────────────────
Rule-based gesture classifier using MediaPipe hand landmark positions.

Supported gestures:
  - Thumbs Up   : thumb up, all fingers curled
  - Fist        : all fingers + thumb curled
  - Open Palm   : all fingers + thumb extended
  - Peace Sign  : index + middle up, rest down
  - Rock Sign   : index + pinky up, middle + ring down, thumb curled
  - Love Sign   : thumb + index + pinky up, middle + ring down
  - Hang Loose  : thumb + pinky up, index + middle + ring down
  - Pointing Up : only index finger up, rest curled
"""


class GestureClassifier:
    FINGER_TIPS = [8, 12, 16, 20]   # index, middle, ring, pinky
    FINGER_PIPS = [6, 10, 14, 18]

    def classify_new(self, hand_landmarks) -> str:
        return self._detect(hand_landmarks)

    def classify(self, hand_landmarks) -> str:
        return self._detect(hand_landmarks.landmark)

    def _detect(self, lm) -> str:
        f = self._fingers_up(lm)   # [index, middle, ring, pinky]
        t = self._thumb_up(lm)

        index, middle, ring, pinky = f

        # ── Open Palm: all up ─────────────────────────────────────────────────
        if t and index and middle and ring and pinky:
            return "Open Palm"

        # ── Fist: all down ────────────────────────────────────────────────────
        if not t and not any(f):
            return "Fist"

        # ── Thumbs Up: only thumb ─────────────────────────────────────────────
        if t and not any(f):
            return "Thumbs Up"

        # ── Peace Sign: index + middle ────────────────────────────────────────
        if not t and index and middle and not ring and not pinky:
            return "Peace Sign"

        # ── Pointing Up: only index ───────────────────────────────────────────
        if not t and index and not middle and not ring and not pinky:
            return "Pointing Up"

        # ── Rock Sign: index + pinky ──────────────────────────────────────────
        if not t and index and not middle and not ring and pinky:
            return "Rock Sign"

        # ── Hang Loose: thumb + pinky ─────────────────────────────────────────
        if t and not index and not middle and not ring and pinky:
            return "Hang Loose"

        # ── Love Sign: thumb + index + pinky ─────────────────────────────────
        if t and index and not middle and not ring and pinky:
            return "Love Sign"

        return "Unknown"

    def _fingers_up(self, lm) -> list:
        return [lm[tip].y < lm[pip].y
                for tip, pip in zip(self.FINGER_TIPS, self.FINGER_PIPS)]

    def _thumb_up(self, lm) -> bool:
        tip           = lm[4]
        ip            = lm[3]
        mcp           = lm[2]
        vertical_ok   = tip.y < ip.y - 0.02
        palm_center_x = (lm[5].x + lm[17].x) / 2
        horizontal_ok = abs(tip.x - palm_center_x) > abs(mcp.x - palm_center_x)
        return vertical_ok and horizontal_ok