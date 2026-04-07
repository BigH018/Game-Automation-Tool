import threading

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit,
    QDoubleSpinBox, QSpinBox, QScrollArea, QFrame,
)

from ui.helpers import _section

try:
    import sounddevice as _sd
except ImportError:
    _sd = None


class SettingsTabMixin:
    """Mixin providing Settings tab builder methods for MainWindow."""

    def _build_tab_settings(self) -> QWidget:
        """Settings tab — all configuration grouped into sub-sections."""
        content = QWidget()
        v = QVBoxLayout(content)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)

        v.addWidget(_section("Audio Settings"))
        v.addWidget(self._build_audio_settings())

        v.addSpacing(8)
        v.addWidget(_section("Device Settings"))
        v.addWidget(self._build_device_settings())

        v.addSpacing(8)
        v.addWidget(_section("Game Controls"))
        v.addWidget(self._build_game_controls())

        v.addSpacing(8)
        v.addWidget(_section("Hotkey"))
        v.addWidget(self._build_hotkey_settings())

        v.addSpacing(8)
        v.addWidget(_section("Notifications"))
        v.addWidget(self._build_notification_settings())

        v.addStretch()

        # Wrap in a scroll area so settings never get clipped on small windows
        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        return scroll

    def _build_audio_settings(self) -> QWidget:
        w = QWidget()
        g = QGridLayout(w)
        g.setContentsMargins(0, 6, 0, 6)
        g.setHorizontalSpacing(10)
        g.setVerticalSpacing(10)

        g.addWidget(QLabel("WAV file"), 0, 0)
        self.edit_wav = QLineEdit(self.core.wav_file)
        self.edit_wav.setPlaceholderText("alert.wav")
        self.edit_wav.textChanged.connect(lambda v: setattr(self.core, "wav_file", v))

        btn_browse = QPushButton("Browse")
        btn_browse.setObjectName("btn_browse")
        btn_browse.clicked.connect(self._browse_wav)

        row = QHBoxLayout()
        row.setSpacing(6)
        row.addWidget(self.edit_wav)
        row.addWidget(btn_browse)
        g.addLayout(row, 0, 1)

        g.addWidget(QLabel("Threshold"), 1, 0)
        self.spin_threshold = QDoubleSpinBox()
        self.spin_threshold.setRange(0.01, 1.0)
        self.spin_threshold.setSingleStep(0.01)
        self.spin_threshold.setDecimals(2)
        self.spin_threshold.setValue(self.core.threshold)
        self.spin_threshold.valueChanged.connect(lambda v: setattr(self.core, "threshold", v))
        g.addWidget(self.spin_threshold, 1, 1)

        g.setColumnStretch(1, 1)
        return w

    def _build_device_settings(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(0, 6, 0, 6)
        outer.setSpacing(10)

        btn_scan = QPushButton("Scan Devices")
        btn_scan.setObjectName("btn_scan")
        btn_scan.clicked.connect(self._scan_devices)
        outer.addWidget(btn_scan)

        inner = QWidget()
        g = QGridLayout(inner)
        g.setContentsMargins(0, 0, 0, 0)
        g.setHorizontalSpacing(10)
        g.setVerticalSpacing(10)

        g.addWidget(QLabel("Device index"), 0, 0)
        self.spin_device = QSpinBox()
        self.spin_device.setRange(0, 64)
        self.spin_device.setValue(self.core.device)
        self.spin_device.valueChanged.connect(lambda v: setattr(self.core, "device", v))
        g.addWidget(self.spin_device, 0, 1)

        g.addWidget(QLabel("Sample rate"), 1, 0)
        self.spin_sr = QSpinBox()
        self.spin_sr.setRange(8000, 192000)
        self.spin_sr.setSingleStep(1000)
        self.spin_sr.setValue(self.core.samplerate)
        self.spin_sr.valueChanged.connect(lambda v: setattr(self.core, "samplerate", v))
        g.addWidget(self.spin_sr, 1, 1)

        g.setColumnStretch(1, 1)
        outer.addWidget(inner)
        return w

    def _build_game_controls(self) -> QWidget:
        """A Button (Confirm) rebind row in the Settings tab."""
        macro = self.core.sweet_scent

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 6, 0, 6)
        v.setSpacing(10)

        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        h.addWidget(QLabel("A Button (Confirm)"))

        self._lbl_a_button_key = QLabel(macro.a_button_key.upper())
        self._lbl_a_button_key.setObjectName("key_value")

        self._btn_a_button_rebind = QPushButton("Rebind")
        self._btn_a_button_rebind.setObjectName("btn_rebind")
        self._btn_a_button_rebind.setProperty("rebinding", "false")
        self._btn_a_button_rebind.clicked.connect(
            lambda checked=False: self._start_game_key_rebind(
                "a_button_key", self._lbl_a_button_key, self._btn_a_button_rebind
            )
        )

        h.addWidget(self._lbl_a_button_key)
        h.addStretch()
        h.addWidget(self._btn_a_button_rebind)
        v.addWidget(row)

        return w

    def _build_hotkey_settings(self) -> QWidget:
        """Four hotkey rows in the Settings tab — one per macro mode."""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 4, 0, 4)
        v.setSpacing(8)

        slot_labels = [
            ("sweet_scent",   "Sweet Scent key"),
            ("berry",         "Berry Farming key"),
            ("singles",       "Singles Farming key"),
            ("gtl",           "GTL Sniper key"),
            ("gym_run",       "Gym Run key"),
            ("trainer_run",   "Trainer Run key"),
            ("fishing",       "Fishing key"),
            ("free_shunt",    "Free Shunt key"),
            ("kill_switch",   "Kill Switch key"),
        ]
        for slot, label_text in slot_labels:
            v.addWidget(self._build_hotkey_row(slot, label_text))
        return w

    def _build_notification_settings(self) -> QWidget:
        """Discord webhook notification settings."""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 4, 0, 4)
        v.setSpacing(10)

        # Enable toggle
        toggle_row = QWidget()
        th = QHBoxLayout(toggle_row)
        th.setContentsMargins(0, 0, 0, 0)
        th.setSpacing(10)

        self._btn_notif_toggle = QPushButton("Disabled")
        self._btn_notif_toggle.setObjectName("btn_notif_toggle")
        self._btn_notif_toggle.setProperty("notif_on", "false")
        self._btn_notif_toggle.clicked.connect(self._toggle_notifications)

        th.addWidget(QLabel("Discord notifications"))
        th.addStretch()
        th.addWidget(self._btn_notif_toggle)
        v.addWidget(toggle_row)

        # Webhook URL + Test button
        url_row = QWidget()
        uh = QHBoxLayout(url_row)
        uh.setContentsMargins(0, 0, 0, 0)
        uh.setSpacing(6)

        self._edit_webhook = QLineEdit()
        self._edit_webhook.setPlaceholderText("Paste your Discord webhook URL here")

        self._btn_notif_test = QPushButton("Test")
        self._btn_notif_test.setObjectName("btn_notif_test")
        self._btn_notif_test.setEnabled(bool(self.nm.webhook_url))
        self._btn_notif_test.clicked.connect(self._send_test_notification)

        self._edit_webhook.textChanged.connect(self._on_webhook_url_changed)
        if self.nm.webhook_url:
            self._edit_webhook.setText(self.nm.webhook_url)

        uh.addWidget(self._edit_webhook)
        uh.addWidget(self._btn_notif_test)
        v.addWidget(url_row)

        return w

    def _toggle_notifications(self):
        """Flip Discord notifications on/off and update the button."""
        if self.nm is None:
            return
        self.nm.enabled = not self.nm.enabled
        on = self.nm.enabled
        self._btn_notif_toggle.setText("Enabled" if on else "Disabled")
        self._btn_notif_toggle.setProperty("notif_on", "true" if on else "false")
        self._btn_notif_toggle.setStyle(self._btn_notif_toggle.style())

    def _on_webhook_url_changed(self, text: str):
        """Sync the URL to the NotificationManager and enable/disable Test."""
        if self.nm is not None:
            self.nm.webhook_url = text.strip()
        self._btn_notif_test.setEnabled(bool(text.strip()))

    def _send_test_notification(self):
        """Send a test message through the webhook."""
        if self.nm is None:
            return
        if not self.nm.webhook_url:
            self._append_log("No webhook URL set — paste a URL first.")
            return
        self._append_log(f"Sending test notification to webhook…")
        self.nm.send_test_message()

    # ── Device scanner ─────────────────────────────────────────

    def _scan_devices(self):
        """Kick off a non-blocking device scan in a background thread."""
        threading.Thread(target=self._run_scan, daemon=True).start()

    _SCAN_RATES = [44100, 48000, 96000, 192000]

    def _run_scan(self):
        """Enumerate input devices, test supported sample rates, emit to log (background thread)."""
        if _sd is None:
            self.signals.log_message.emit("Device scan unavailable: sounddevice not installed.")
            return

        self.signals.log_message.emit("── Audio Input Devices ──────────────────")
        try:
            devices = _sd.query_devices()
            try:
                default_in = _sd.default.device[0]
            except Exception:
                default_in = -1

            found = False
            for idx, dev in enumerate(devices):
                if dev["max_input_channels"] == 0:
                    continue

                marker = " (default input)" if idx == default_in else ""
                self.signals.log_message.emit(f"  [{idx}] {dev['name']}{marker}")

                supported = []
                for rate in self._SCAN_RATES:
                    try:
                        _sd.check_input_settings(device=idx, samplerate=rate)
                        supported.append(str(rate))
                    except Exception:
                        pass

                rate_str = ", ".join(supported) if supported else "unknown"
                self.signals.log_message.emit(f"      Supported rates: {rate_str}")
                found = True

            if not found:
                self.signals.log_message.emit("  No input devices found.")

            self.signals.log_message.emit(
                "Device tip: Look for 'Stereo Mix' or 'Line In' if you are using a "
                "capture card or line-in cable. Not sure which to pick? Try the "
                "default input first and see if detection works."
            )
            self.signals.log_message.emit(
                "Sample rate tip: 48000 Hz works for most setups. A mismatch between "
                "your device's supported rate and the Sample Rate field is the most "
                "common reason the shiny sound is not detected — make sure they match."
            )
        except Exception as exc:
            self.signals.log_message.emit(f"Scan error: {exc}")
