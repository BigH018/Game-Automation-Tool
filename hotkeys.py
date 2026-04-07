"""
hotkeys.py — Global keyboard listener with rebindable per-mode toggle keys.
Communicates with the UI via Qt signals to stay thread-safe.
"""

from pynput import keyboard as pynput_kb
from PyQt5.QtCore import QObject, pyqtSignal


class _Signals(QObject):
    toggle              = pyqtSignal()     # Sweet Scent — wired to core in main.py
    toggle_berry        = pyqtSignal()     # Berry Farming
    toggle_singles      = pyqtSignal()     # Singles Farming
    toggle_gtl          = pyqtSignal()     # GTL Sniper
    toggle_gym_run      = pyqtSignal()     # Gym Run
    toggle_trainer_run  = pyqtSignal()     # Trainer Run
    toggle_fishing      = pyqtSignal()     # Fishing
    toggle_free_shunt   = pyqtSignal()     # Free Shunt
    toggle_egg_hatching = pyqtSignal()     # Egg Hatching
    quit           = pyqtSignal()
    rebind_done    = pyqtSignal(str, str)  # (slot_name, key_name) — key_name="" if cancelled


class HotkeyManager:
    """
    Runs a daemon pynput listener that fires Qt signals on toggle / quit.
    Supports three independently rebindable slots: sweet_scent, berry, singles.
    """

    # Default key per slot
    DEFAULTS = {
        "sweet_scent":   pynput_kb.Key.f9,
        "berry":         pynput_kb.Key.f8,
        "singles":       pynput_kb.Key.f7,
        "gtl":           pynput_kb.Key.f6,
        "gym_run":       pynput_kb.Key.f5,
        "trainer_run":   pynput_kb.Key.f4,
        "fishing":       pynput_kb.Key.f3,
        "free_shunt":    pynput_kb.Key.f2,
        "egg_hatching":  pynput_kb.Key.f1,
        "kill_switch":   pynput_kb.Key.f10,
    }

    def __init__(self):
        self.signals         = _Signals()
        self._keys           = dict(self.DEFAULTS)   # slot → pynput key
        self._rebinding_slot = None                  # slot currently being rebound, or None
        self._listener       = None

    # ── Public API ────────────────────────────────────────────

    @property
    def toggle_key_name(self) -> str:
        """Backward compat — human-readable name for the Sweet Scent key."""
        return self.key_name("sweet_scent")

    def key_name(self, slot: str) -> str:
        """Human-readable name for the given slot's current key (e.g. 'F9')."""
        return self._format_key(self._keys[slot])

    def _format_key(self, key) -> str:
        if isinstance(key, pynput_kb.Key):
            return key.name.upper()
        if getattr(key, "char", None):
            return key.char.upper()
        return f"VK{key.vk}"

    def start_rebind(self, slot: str = "sweet_scent"):
        """Begin listening for the next key press as the new key for slot."""
        self._rebinding_slot = slot

    def cancel_rebind(self):
        """Cancel any in-progress rebind without changing any key."""
        self._rebinding_slot = None

    def set_key_by_name(self, name: str, slot: str = "sweet_scent") -> bool:
        """
        Set a slot's key from a name string (e.g. 'F9', 'A').
        Returns True if the key was recognised and applied.
        """
        try:
            self._keys[slot] = pynput_kb.Key[name.lower()]
            return True
        except KeyError:
            pass
        if len(name) == 1:
            self._keys[slot] = pynput_kb.KeyCode.from_char(name.lower())
            return True
        return False

    # ── Listener ──────────────────────────────────────────────

    def _on_press(self, key):
        if self._rebinding_slot is not None:
            slot = self._rebinding_slot
            if key == pynput_kb.Key.esc:
                # Cancel — do NOT quit the app
                self._rebinding_slot = None
                self.signals.rebind_done.emit(slot, "")
            else:
                self._keys[slot]     = key
                self._rebinding_slot = None
                self.signals.rebind_done.emit(slot, self.key_name(slot))
            return

        if key == self._keys["sweet_scent"]:
            self.signals.toggle.emit()
        elif key == self._keys["berry"]:
            self.signals.toggle_berry.emit()
        elif key == self._keys["singles"]:
            self.signals.toggle_singles.emit()
        elif key == self._keys["gtl"]:
            self.signals.toggle_gtl.emit()
        elif key == self._keys["gym_run"]:
            self.signals.toggle_gym_run.emit()
        elif key == self._keys["trainer_run"]:
            self.signals.toggle_trainer_run.emit()
        elif key == self._keys["fishing"]:
            self.signals.toggle_fishing.emit()
        elif key == self._keys["free_shunt"]:
            self.signals.toggle_free_shunt.emit()
        elif key == self._keys["egg_hatching"]:
            self.signals.toggle_egg_hatching.emit()
        elif key == self._keys["kill_switch"]:
            self.signals.quit.emit()

    def start(self):
        self._listener = pynput_kb.Listener(on_press=self._on_press)
        self._listener.daemon = True
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
