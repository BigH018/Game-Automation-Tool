"""
egg_hatching.py — EggHatchingMacro: automates egg-hatching box operations.

Works through a 6-row x 10-column grid in row-pairs:
  Pass 1: R1+R2 columns 1→10  (10 iterations)
  Pass 2: R3+R4 columns 1→10  (10 iterations)
  Pass 3: R5+R6 columns 1→10  (10 iterations)
  = 30 iterations per box

Each iteration:
  E → wait → E → Ctrl+Click slot A → Ctrl+Click slot B → Click confirm → E → E → E
"""

import time, random, threading

try:
    import interception
except ImportError:
    raise ImportError("interception-python is not installed. Run: pip install interception-python")


class EggHatchingMacro:
    """
    Automates the egg-hatching grid loop.
    Communicates with the coordinator via on_start, on_stop, and on_log callbacks.
    """

    def __init__(self):
        self.running       = False
        self._stop_event   = threading.Event()
        self._macro_thread = None

        # Grid reference points — (x, y) screen coords of cell centres
        self.grid_top_left     = (704, 395)    # centre of R1 C1
        self.grid_bottom_right = (1513, 776)   # centre of R6 C10

        # Fixed click target — (x, y) screen coords
        self.confirm_coords = (1338, 721)

        # Game key
        self.use_key = "e"

        # Delays (milliseconds)
        self.text_delay_min   = 1500
        self.text_delay_max   = 2000
        self.action_delay_min = 200
        self.action_delay_max = 400
        self.egg_wait_min     = 2000
        self.egg_wait_max     = 2500

        self.debug = False

        # Callbacks — set by the coordinator
        self.on_start = None
        self.on_stop  = None
        self.on_log   = None

    # ── Helpers ───────────────────────────────────────────────

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def _tap(self, key: str):
        interception.press(key)

    def _wait_text(self) -> int:
        ms = random.randint(self.text_delay_min, self.text_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _wait_action(self) -> int:
        ms = random.randint(self.action_delay_min, self.action_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _wait_egg(self) -> int:
        ms = random.randint(self.egg_wait_min, self.egg_wait_max)
        time.sleep(ms / 1000)
        return ms

    def _click(self, coords: tuple):
        """Move to (x, y) and left-click."""
        x, y = coords
        interception.move_to(x, y)
        time.sleep(0.05)
        interception.left_click()

    def _ctrl_click(self, coords: tuple):
        """Hold Ctrl, move to (x, y), left-click, release Ctrl."""
        x, y = coords
        interception.key_down("ctrlleft")
        time.sleep(0.05)
        interception.move_to(x, y)
        time.sleep(0.05)
        interception.left_click()
        time.sleep(0.05)
        interception.key_up("ctrlleft")

    # ── Grid maths ────────────────────────────────────────────

    def _cell_coords(self, row: int, col: int) -> tuple:
        """
        Return screen (x, y) for a grid cell.
        row: 0-5 (R1-R6), col: 0-9 (C1-C10).
        Linearly interpolates between grid_top_left and grid_bottom_right.
        """
        x1, y1 = self.grid_top_left
        x2, y2 = self.grid_bottom_right
        x = x1 + (x2 - x1) * col / 9   if col < 9 else x2
        y = y1 + (y2 - y1) * row / 5    if row < 5 else y2
        # Handle edge: col=9 means rightmost, row=5 means bottommost
        x = x1 + (x2 - x1) * col / 9
        y = y1 + (y2 - y1) * row / 5
        return (int(x), int(y))

    # ── Single iteration ──────────────────────────────────────

    def _do_iteration(self, slot_a: tuple, slot_b: tuple, label_a: str, label_b: str):
        """
        One macro loop:
        E → text wait → E → Ctrl+Click A → Ctrl+Click B → Click confirm → E → E → E
        """
        # 1. Press E (interact)
        self._tap(self.use_key)
        ms = self._wait_text()
        if self.debug:
            self._log(f"[DEBUG] Pressed E — text delay {ms}ms")
        if not self.running:
            return

        # 2. Press E (advance text)
        self._tap(self.use_key)
        ms = self._wait_action()
        if self.debug:
            self._log(f"[DEBUG] Pressed E — action delay {ms}ms")
        if not self.running:
            return

        # 3. Ctrl+Left Click slot A
        self._ctrl_click(slot_a)
        ms = self._wait_action()
        if self.debug:
            self._log(f"[DEBUG] Ctrl+Click {label_a} {slot_a} — {ms}ms")
        if not self.running:
            return

        # 4. Ctrl+Left Click slot B
        self._ctrl_click(slot_b)
        ms = self._wait_action()
        if self.debug:
            self._log(f"[DEBUG] Ctrl+Click {label_b} {slot_b} — {ms}ms")
        if not self.running:
            return

        # 5. Left Click confirm area
        self._click(self.confirm_coords)
        ms = self._wait_action()
        if self.debug:
            self._log(f"[DEBUG] Click confirm {self.confirm_coords} — {ms}ms")
        if not self.running:
            return

        # 6. Press E then wait for egg
        self._tap(self.use_key)
        ms = self._wait_egg()
        if self.debug:
            self._log(f"[DEBUG] Pressed E — egg wait {ms}ms")
        if not self.running:
            return

        # 7. Press E (text box)
        self._tap(self.use_key)
        ms = self._wait_text()
        if self.debug:
            self._log(f"[DEBUG] Pressed E — text delay {ms}ms")
        if not self.running:
            return

        # 8. Press E (text box)
        self._tap(self.use_key)
        ms = self._wait_text()
        if self.debug:
            self._log(f"[DEBUG] Pressed E — text delay {ms}ms")
        if not self.running:
            return

    # ── Main loop ─────────────────────────────────────────────

    def _run_macro(self):
        interception.auto_capture_devices()
        time.sleep(0.1)

        if not self.grid_top_left or not self.grid_bottom_right:
            self._log("Grid not configured — set Top-Left and Bottom-Right cells first.")
            self._finish()
            return

        if not self.confirm_coords:
            self._log("Confirm click target not set — capture it first.")
            self._finish()
            return

        iteration = 0
        # Process row-pairs: (R1,R2), (R3,R4), (R5,R6)
        for pair_start in (0, 2, 4):
            row_a = pair_start
            row_b = pair_start + 1
            for col in range(10):
                if not self.running:
                    self._finish()
                    return

                iteration += 1
                coords_a = self._cell_coords(row_a, col)
                coords_b = self._cell_coords(row_b, col)
                label_a  = f"R{row_a + 1}C{col + 1}"
                label_b  = f"R{row_b + 1}C{col + 1}"

                self._log(f"Iteration {iteration}/30 — {label_a} + {label_b}")
                self._do_iteration(coords_a, coords_b, label_a, label_b)

        self._finish()

    def _finish(self):
        self.running = False
        self._log("Macro stopped.")
        if self.on_stop:
            self.on_stop()

    # ── Public API ────────────────────────────────────────────

    def start(self):
        if self.running:
            return
        self._stop_event.clear()
        self.running = True
        self._macro_thread = threading.Thread(target=self._run_macro, daemon=True)
        self._macro_thread.start()
        self._log("Egg Hatching macro started.")
        if self.on_start:
            self.on_start()

    def stop(self):
        self.running = False
        self._stop_event.set()
