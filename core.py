import os, sys, time, threading, wave
import numpy as np
from math import gcd
from scipy.signal import correlate, resample_poly
import sounddevice as sd

from sweet_scent     import SweetScentMacro
from berry_farming   import BerryFarmingMacro
from singles_farming import SinglesFarmingMacro
from gtl_sniper      import GTLSniperMacro
from gym_run         import GymRunMacro
from trainer_run     import TrainerRunMacro
from fishing         import FishingMacro
from free_shunt      import FreeShuntMacro
from egg_hatching    import EggHatchingMacro


class MacroCore:
    """
    Coordinates the three macro modules and audio detection.
    Communicate with the UI exclusively through the on_* callbacks.
    """

    def __init__(self):
        self.running = False

        # ── Configurable settings (edit via UI or directly) ──
        self.wav_file   = self._default_wav_path()
        self.threshold  = 0.3
        self.device     = 2
        self.samplerate = 48000

        # ── Audio stop event — set() to kill the current listener ──
        self._audio_stop = threading.Event()

        # ── Macro instances ──
        self.sweet_scent     = SweetScentMacro()
        self.berry_farming   = BerryFarmingMacro()
        self.singles_farming = SinglesFarmingMacro()
        self.gtl_sniper      = GTLSniperMacro()
        self.gym_run         = GymRunMacro()
        self.trainer_run     = TrainerRunMacro()
        self.fishing         = FishingMacro()
        self.free_shunt      = FreeShuntMacro()
        self.egg_hatching    = EggHatchingMacro()

        self._active_macro = None
        self.active_mode   = None   # last mode passed to start(); read by UI

        # ── Notification manager (set by main.py) ──
        self.notification_manager = None

        # ── UI callbacks (set by the UI layer) ──
        self.on_start          = None   # ()
        self.on_stop           = None   # ()
        self.on_shiny_detected = None   # (score: float)
        self.on_log            = None   # (message: str)

        # Route each macro's callbacks through this coordinator
        for macro in (self.sweet_scent, self.berry_farming, self.singles_farming,
                      self.gtl_sniper, self.gym_run, self.trainer_run,
                      self.fishing, self.free_shunt, self.egg_hatching):
            macro.on_log   = self._log
            macro.on_start = self._on_macro_start
            macro.on_stop  = self._on_macro_stop

    # ── Internal helpers ─────────────────────────────────────

    @staticmethod
    def _default_wav_path() -> str:
        """
        Resolve the default alert.wav location.

        Search order:
        1. alert.wav next to the .exe (zip-packaged layout — user can replace it)
        2. alert.wav inside the PyInstaller bundle (sys._MEIPASS)
        3. alert.wav next to this source file (running from source)
        """
        candidates = []
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(sys.executable)
            candidates.append(os.path.join(exe_dir, "alert.wav"))
            meipass = getattr(sys, "_MEIPASS", None)
            if meipass:
                candidates.append(os.path.join(meipass, "alert.wav"))
        else:
            candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "alert.wav"))

        for path in candidates:
            if os.path.isfile(path):
                return path
        return candidates[0] if candidates else "alert.wav"

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def _on_macro_start(self):
        self.running = True
        if self.on_start:
            self.on_start()

    def _on_macro_stop(self):
        self.running = False
        if self.on_stop:
            self.on_stop()

    # ── Macro control ────────────────────────────────────────

    def start(self, mode: str = "sweet_scent"):
        if self.running:
            return
        macro_map = {
            "sweet_scent":     self.sweet_scent,
            "berry_farming":   self.berry_farming,
            "singles_farming": self.singles_farming,
            "gtl_sniper":      self.gtl_sniper,
            "gym_run":         self.gym_run,
            "trainer_run":     self.trainer_run,
            "fishing":         self.fishing,
            "free_shunt":      self.free_shunt,
            "egg_hatching":    self.egg_hatching,
        }
        self.active_mode   = mode
        self._active_macro = macro_map.get(mode)
        if self._active_macro:
            self._active_macro.start()

    def stop(self):
        self.running = False
        if self._active_macro:
            self._active_macro.stop()

    # ── Audio detection ──────────────────────────────────────

    def _load_wav(self, path: str) -> np.ndarray:
        with wave.open(path) as f:
            n_ch, orig_rate = f.getnchannels(), f.getframerate()
            raw = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32)
        if n_ch > 1:
            raw = raw.reshape(-1, n_ch).mean(axis=1)
        if orig_rate != self.samplerate:
            g = gcd(orig_rate, self.samplerate)
            raw = resample_poly(raw, self.samplerate // g, orig_rate // g)
        raw /= (np.max(np.abs(raw)) + 1e-9)
        return raw

    def start_audio(self):
        """Load the WAV template and begin listening on the configured device.

        Safe to call multiple times — stops any existing listener first.
        Returns silently if no WAV file has been selected yet.
        """
        import os
        if not self.wav_file or not os.path.isfile(self.wav_file):
            self._log("Audio: no WAV file set — browse to one in Settings → Audio Settings.")
            return

        # Stop any previously running listener
        self._audio_stop.set()
        stop = threading.Event()
        self._audio_stop = stop

        target      = self._load_wav(self.wav_file)
        target_norm = np.linalg.norm(target)
        buf         = np.zeros(len(target) * 2, np.float32)
        last_hit    = [0.0]

        def callback(indata, frames, t, status):
            chunk = indata[:, 0] if indata.ndim > 1 else indata[:].copy()
            buf[:] = np.roll(buf, -len(chunk))
            buf[-len(chunk):] = chunk
            bn = np.linalg.norm(buf)
            if bn < 0.01:
                return
            score = float(
                np.max(correlate(buf, target, mode="valid"))
                / (bn * target_norm + 1e-9)
            )
            now = time.time()
            if self.running and score >= self.threshold and now - last_hit[0] > 2.0:
                last_hit[0] = now
                self._log(f"✦ SHINY DETECTED  (score: {score:.4f})")
                if self.notification_manager:
                    self.notification_manager.send_shiny_alert(score)
                if self.on_shiny_detected:
                    self.on_shiny_detected(score)
                self.stop()

        def _run():
            with sd.InputStream(
                device=self.device,
                channels=2,
                samplerate=self.samplerate,
                dtype="float32",
                blocksize=1024,
                callback=callback,
            ):
                stop.wait()

        threading.Thread(target=_run, daemon=True).start()
        self._log(f"Audio listener active — device {self.device}, threshold {self.threshold}")
