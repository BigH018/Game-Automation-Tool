"""
singles_farming.py — SinglesFarmingMacro: walk-and-encounter farming with battle detection.

Loop:
  1. Capture a reference snapshot of the hotbar region (overworld state).
  2. Hold A (left) for a random walk duration, polling the hotbar for changes.
  3. If no battle, hold D (right) for a random walk duration, polling again.
  4. When the hotbar region changes beyond a brightness threshold → battle detected.
  5. Flee the battle (randomised S/D/A-button order, same as Sweet Scent).
  6. Wait a random battle-end delay, then repeat.

Uses the Interception kernel-level driver for all key input and PIL.ImageGrab
+ numpy for screen-region comparison — no new dependencies.
"""

import time, random, threading
import numpy as np

try:
    import interception
except ImportError:
    raise ImportError("interception-python is not installed. Run: pip install interception-python")

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None


# ── Battle detection ─────────────────────────────────────────────────────────
# Mean absolute pixel difference (0–255 scale) between the reference hotbar
# snapshot and the current frame.  Values above this indicate the hotbar has
# changed (battle started).  30 is conservative — the overworld-to-battle
# shift typically produces diffs of 40–80+.
_BATTLE_THRESHOLD = 30


class SinglesFarmingMacro:
    """
    Walks back and forth to trigger random wild encounters, detects battle
    start via hotbar-region monitoring, flees, and repeats.
    Uses the Interception kernel-level driver for all key input.
    Communicates with the coordinator via on_start, on_stop, and on_log callbacks.
    """

    def __init__(self):
        self.running       = False
        self._stop_event   = threading.Event()
        self._macro_thread = None

        # Configurable game key (shared with Sweet Scent via Settings tab)
        self.a_button_key = "e"

        # Configurable walk timing (ms)
        self.walk_duration_min = 400
        self.walk_duration_max = 900

        # Configurable flee key-press delay (ms)
        self.key_press_delay_min = 28
        self.key_press_delay_max = 160

        # Configurable battle-start delay (ms) — wait for battle to fully load
        self.battle_start_delay_min = 10000
        self.battle_start_delay_max = 11000

        # Configurable battle-end delay (ms)
        self.battle_end_delay_min = 1800
        self.battle_end_delay_max = 4500

        # Battle detection
        self.poll_interval = 100   # ms — how often to sample the hotbar
        self.hotbar_region = (363, 33, 43, 57)  # (x, y, w, h) screen region to monitor

        # Debug mode — set by the UI toggle, never persisted
        self.debug = False

        # Callbacks — set by the coordinator
        self.on_start = None   # ()
        self.on_stop  = None   # ()
        self.on_log   = None   # (message: str)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def _tap(self, key: str):
        interception.press(key)

    def _wait(self, ms_min: int, ms_max: int) -> int:
        """Sleep for a random duration, respecting the stop event. Returns the delay used in ms."""
        ms = random.randint(ms_min, ms_max)
        self._stop_event.wait(timeout=ms / 1000)
        return ms

    def _capture_region(self) -> np.ndarray | None:
        """Grab the hotbar region as a numpy array. Returns None on failure."""
        if self.hotbar_region is None or ImageGrab is None:
            return None
        x, y, w, h = self.hotbar_region
        try:
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            return np.array(img, dtype=np.float32)
        except Exception:
            return None

    def _detect_battle(self, reference: np.ndarray) -> bool:
        """Compare current hotbar snapshot to reference. Returns True if battle detected."""
        current = self._capture_region()
        if current is None or reference is None:
            return False
        if current.shape != reference.shape:
            return False
        diff = float(np.mean(np.abs(current - reference)))
        if self.debug:
            self._log(f"[DEBUG] Hotbar diff: {diff:.1f}")
        return diff > _BATTLE_THRESHOLD

    # ── Walking with battle polling ───────────────────────────────────────────

    def _walk_and_poll(self, direction: str, reference: np.ndarray) -> bool:
        """
        Hold a direction key for a random walk duration while polling for battle.
        Returns True if a battle was detected during the walk.
        """
        walk_ms = random.randint(self.walk_duration_min, self.walk_duration_max)
        if self.debug:
            self._log(f"[DEBUG] Walking {direction.upper()} for {walk_ms}ms")

        interception.key_down(direction)
        elapsed = 0
        poll_ms = self.poll_interval

        while elapsed < walk_ms and not self._stop_event.is_set():
            remaining = walk_ms - elapsed
            sleep_ms = min(poll_ms, remaining)
            self._stop_event.wait(timeout=sleep_ms / 1000)
            elapsed += sleep_ms

            if self._stop_event.is_set():
                break

            if self._detect_battle(reference):
                interception.key_up(direction)
                if self.debug:
                    self._log(f"[DEBUG] Battle detected after {elapsed}ms of walking")
                return True

        interception.key_up(direction)
        return False

    # ── Flee sequence ─────────────────────────────────────────────────────────

    def _flee_sequence(self):
        """Flee the battle — identical to Sweet Scent's randomised flee logic."""
        if random.choice([True, False]):
            self._tap("s")
            kp_ms = self._wait(self.key_press_delay_min, self.key_press_delay_max)
            if self.debug:
                self._log(f"[DEBUG] Pressed S — after {kp_ms}ms")

            self._tap("d")
            kp_ms = self._wait(self.key_press_delay_min, self.key_press_delay_max)
            if self.debug:
                self._log(f"[DEBUG] Pressed D — after {kp_ms}ms")

            self._tap(self.a_button_key)
            kp_ms = self._wait(self.key_press_delay_min, self.key_press_delay_max)
            if self.debug:
                self._log(f"[DEBUG] Pressed A Button ({self.a_button_key.upper()}) — after {kp_ms}ms")
        else:
            self._tap("d")
            kp_ms = self._wait(self.key_press_delay_min, self.key_press_delay_max)
            if self.debug:
                self._log(f"[DEBUG] Pressed D — after {kp_ms}ms")

            self._tap("s")
            kp_ms = self._wait(self.key_press_delay_min, self.key_press_delay_max)
            if self.debug:
                self._log(f"[DEBUG] Pressed S — after {kp_ms}ms")

            self._tap(self.a_button_key)
            kp_ms = self._wait(self.key_press_delay_min, self.key_press_delay_max)
            if self.debug:
                self._log(f"[DEBUG] Pressed A Button ({self.a_button_key.upper()}) — after {kp_ms}ms")

    # ── Macro loop ────────────────────────────────────────────────────────────

    def _run_macro(self):
        if ImageGrab is None:
            self._log("Singles Farming: Pillow not installed — screen capture unavailable. "
                      "Run: pip install Pillow")
            self.running = False
            if self.on_stop:
                self.on_stop()
            return

        if self.hotbar_region is None:
            self._log("Singles Farming: Hotbar region not set — use Set Region on the Singles Farming tab.")
            self.running = False
            if self.on_stop:
                self.on_stop()
            return

        interception.auto_capture_devices()
        time.sleep(0.1)

        self._log("Singles Farming running — press hotkey to stop.")

        while self.running and not self._stop_event.is_set():
            # Capture reference frame (overworld hotbar)
            reference = self._capture_region()
            if reference is None:
                self._log("Singles Farming: Failed to capture hotbar region.")
                break

            if self.debug:
                self._log("[DEBUG] Reference frame captured — starting walk cycle")

            # Walk left
            if self._walk_and_poll("a", reference):
                self._log("Battle detected — waiting for battle to load…")
                bs_ms = self._wait(self.battle_start_delay_min, self.battle_start_delay_max)
                if self.debug:
                    self._log(f"[DEBUG] Battle start delay — {bs_ms}ms")
                self._flee_sequence()
                be_ms = self._wait(self.battle_end_delay_min, self.battle_end_delay_max)
                if self.debug:
                    self._log(f"[DEBUG] Waiting after battle — {be_ms}ms")
                continue

            if self._stop_event.is_set():
                break

            # Walk right
            if self._walk_and_poll("d", reference):
                self._log("Battle detected — waiting for battle to load…")
                bs_ms = self._wait(self.battle_start_delay_min, self.battle_start_delay_max)
                if self.debug:
                    self._log(f"[DEBUG] Battle start delay — {bs_ms}ms")
                self._flee_sequence()
                be_ms = self._wait(self.battle_end_delay_min, self.battle_end_delay_max)
                if self.debug:
                    self._log(f"[DEBUG] Waiting after battle — {be_ms}ms")
                continue

        self.running = False
        self._log("Singles Farming stopped.")
        if self.on_stop:
            self.on_stop()

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        if self.running:
            return
        self._stop_event.clear()
        self.running = True
        self._macro_thread = threading.Thread(target=self._run_macro, daemon=True)
        self._macro_thread.start()
        self._log("Singles Farming started.")
        if self.on_start:
            self.on_start()

    def stop(self):
        self.running = False
        self._stop_event.set()
