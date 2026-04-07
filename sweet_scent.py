"""
sweet_scent.py — SweetScentMacro: key-press automation for the Sweet Scent method.
"""

import time, random, threading

try:
    import interception
except ImportError:
    raise ImportError("interception-python is not installed. Run: pip install interception-python")


class SweetScentMacro:
    """
    Automates the Sweet Scent encounter loop.
    Communicates with the coordinator via on_start, on_stop, and on_log callbacks.
    """

    def __init__(self):
        self.running       = False
        self._stop_event   = threading.Event()
        self._macro_thread = None

        # Configurable key bindings
        self.sweet_scent_key = "2"   # the move trigger key
        self.a_button_key    = "e"   # the confirm/use key

        # Debug mode — set by the UI toggle, never persisted
        self.debug = False

        # Configurable delays (milliseconds)
        self.key_press_delay_min    = 28
        self.key_press_delay_max    = 160
        self.battle_start_delay_min = 12773
        self.battle_start_delay_max = 14500
        self.battle_end_delay_min   = 1800
        self.battle_end_delay_max   = 4500

        # Callbacks — set by the coordinator
        self.on_start = None   # ()
        self.on_stop  = None   # ()
        self.on_log   = None   # (message: str)

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

    def _run_macro(self):
        interception.auto_capture_devices()
        time.sleep(0.1)

        while self.running and not self._stop_event.is_set():
            self._tap(self.sweet_scent_key)
            kp_ms = self._wait(self.key_press_delay_min, self.key_press_delay_max)
            if self.debug:
                self._log(f"[DEBUG] Pressed Sweet Scent key ({self.sweet_scent_key}) — after {kp_ms}ms")

            bs_ms = self._wait(self.battle_start_delay_min, self.battle_start_delay_max)
            if self.debug:
                self._log(f"[DEBUG] Waiting for battle to load — {bs_ms}ms")

            if self._stop_event.is_set():
                break

            # Randomise key order to avoid detection patterns
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

            be_ms = self._wait(self.battle_end_delay_min, self.battle_end_delay_max)
            if self.debug:
                self._log(f"[DEBUG] Waiting after battle — {be_ms}ms")
                self._log("[DEBUG] Cycle complete — starting next")

        self.running = False
        self._log("Macro stopped.")
        if self.on_stop:
            self.on_stop()

    def start(self):
        if self.running:
            return
        self._stop_event.clear()
        self.running = True
        self._macro_thread = threading.Thread(target=self._run_macro, daemon=True)
        self._macro_thread.start()
        self._log("Macro started.")
        if self.on_start:
            self.on_start()

    def stop(self):
        self.running = False
        self._stop_event.set()
