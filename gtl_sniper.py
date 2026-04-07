"""
gtl_sniper.py — GTLSniperMacro: GTL price-sniping automation.

Loop:
  1. Click the Refresh button at a configurable rate.
  2. OCR the price region.
  3. If price <= max_price, click Buy then press Spacebar to confirm.

Mouse clicks and keyboard use the same kernel-level Interception driver as
the Sweet Scent macro — no SendInput / pyautogui required.

OCR dependencies (must be installed in the same Python environment):
  pip install pytesseract Pillow
  + Tesseract OCR executable: https://github.com/UB-Mannheim/tesseract/wiki
"""

import os, sys, time, threading, random

try:
    import interception
except ImportError:
    raise ImportError("interception-python is not installed. Run: pip install interception-python")


# ── Lazy OCR imports ──────────────────────────────────────────────────────────

def _find_tesseract_exe() -> str | None:
    """
    Locate a tesseract.exe binary.

    Search order:
    1. Portable Tesseract-OCR folder next to the .exe (zip-packaged layout)
    2. Portable Tesseract-OCR folder in the PyInstaller bundle (sys._MEIPASS)
    3. Portable Tesseract-OCR folder next to this source file (dev mode)
    4. Default Windows install path (C:\\Program Files\\Tesseract-OCR)
    """
    candidates = []
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "Tesseract-OCR", "tesseract.exe"))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, "Tesseract-OCR", "tesseract.exe"))
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(here, "Tesseract-OCR", "tesseract.exe"))

    candidates.append(r"C:\Program Files\Tesseract-OCR\tesseract.exe")

    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _get_ocr():
    """Return (pytesseract, ImageGrab) or (None, None) if unavailable."""
    try:
        import pytesseract
        from PIL import ImageGrab
        tess_path = _find_tesseract_exe()
        if tess_path:
            pytesseract.pytesseract.tesseract_cmd = tess_path
            # Also set TESSDATA_PREFIX so the portable bundle finds its own language data
            tessdata_dir = os.path.join(os.path.dirname(tess_path), "tessdata")
            if os.path.isdir(tessdata_dir):
                os.environ["TESSDATA_PREFIX"] = tessdata_dir
        return pytesseract, ImageGrab
    except Exception:
        return None, None


# ── Macro ─────────────────────────────────────────────────────────────────────

class GTLSniperMacro:
    """
    GTL price sniper — refreshes the GTL listing and buys when price <= max_price.
    Uses the Interception kernel-level driver for all mouse and keyboard input.
    Communicates with the coordinator via on_start, on_stop, and on_log callbacks.
    """

    def __init__(self):
        self.running       = False
        self._stop_event   = threading.Event()
        self._macro_thread = None

        # Configurable coordinates (set via UI capture flow)
        self.refresh_coords = (1404, 201)
        self.buy_coords     = (1562, 317)
        self.price_region   = (1089, 299, 144, 44)

        # Configurable thresholds / timing
        self.max_price        = 0    # buy when OCR price <= this; 0 = disabled
        self.refresh_rate_min = 86   # ms — lower bound of random refresh interval
        self.refresh_rate_max = 175  # ms — upper bound of random refresh interval

        # Debug mode — logs every price read; toggled via UI, never persisted
        self.debug = False

        # Callbacks — set by the coordinator
        self.on_start = None   # ()
        self.on_stop  = None   # ()
        self.on_log   = None   # (message: str)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def _click(self, coords: tuple):
        """Move to (x, y) and left-click via the Interception driver."""
        x, y = coords
        interception.move_to(x, y)
        time.sleep(0.05)   # brief settle before click
        interception.left_click()

    def _read_price(self) -> int | None:
        """OCR the price region and return the integer price, or None on failure."""
        pytesseract, ImageGrab = _get_ocr()
        if pytesseract is None or ImageGrab is None:
            return None
        if self.price_region is None:
            return None

        x, y, w, h = self.price_region
        try:
            img  = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            text = pytesseract.image_to_string(
                img,
                config="--psm 7 -c tessedit_char_whitelist=0123456789"
            )
            # Strip any non-digit characters (commas, spaces, newlines)
            digits = "".join(ch for ch in text if ch.isdigit())
            return int(digits) if digits else None
        except Exception as exc:
            self._log(f"[GTL] OCR error: {exc}")
            return None

    # ── Macro loop ────────────────────────────────────────────────────────────

    def _run_macro(self):
        pytesseract, _ = _get_ocr()
        if pytesseract is None:
            self._log("GTL Sniper: pytesseract / Pillow not installed — OCR unavailable. "
                      "Run: pip install pytesseract Pillow")
            self.running = False
            if self.on_stop:
                self.on_stop()
            return

        # Initialise the Interception driver (same as Sweet Scent does)
        interception.auto_capture_devices()
        time.sleep(0.1)

        self._log("GTL Sniper running — press hotkey to stop.")

        while self.running and not self._stop_event.is_set():
            # ── Step 1: click Refresh ────────────────────────────────────────
            if self.refresh_coords:
                try:
                    self._click(self.refresh_coords)
                except Exception as exc:
                    self._log(f"[GTL] Refresh click error: {exc}")

            # ── Wait a random interval before next refresh (interruptible) ───
            wait_ms = random.randint(self.refresh_rate_min, self.refresh_rate_max)
            self._stop_event.wait(timeout=wait_ms / 1000)
            if self._stop_event.is_set():
                break

            # ── Step 2: OCR price ────────────────────────────────────────────
            price = self._read_price()
            if price is None:
                if self.debug:
                    self._log("[GTL] Could not read price — check OCR region and Tesseract install.")
                continue

            if self.max_price <= 0:
                if self.debug:
                    self._log(f"[GTL] Price: {price:,} — max price not set, skipping buy.")
                continue

            if self.debug:
                self._log(f"[GTL] Price: {price:,}  /  Max: {self.max_price:,}")

            # ── Step 3: buy if price is within limit ─────────────────────────
            if price <= self.max_price:
                if self.buy_coords:
                    try:
                        self._click(self.buy_coords)
                    except Exception as exc:
                        self._log(f"[GTL] Buy click error: {exc}")

                try:
                    interception.press("space")
                except Exception as exc:
                    self._log(f"[GTL] Spacebar error: {exc}")

                self._log(f"[GTL] ★ Pokemon bought for {price:,} pokeyen!")

        self.running = False
        self._log("GTL Sniper stopped.")
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
        self._log("GTL Sniper started.")
        if self.on_start:
            self.on_start()

    def stop(self):
        self.running = False
        self._stop_event.set()
