"""
fishing.py — FishingMacro: placeholder for Fishing automation.
"""

import threading


class FishingMacro:
    """Placeholder — logs 'not yet implemented'. stop() works correctly."""

    def __init__(self):
        self.running       = False
        self._stop_event   = threading.Event()
        self._macro_thread = None
        self.debug         = False

        self.on_start = None
        self.on_stop  = None
        self.on_log   = None

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def start(self):
        self._log("Fishing macro not yet implemented.")

    def stop(self):
        self.running = False
        self._stop_event.set()
