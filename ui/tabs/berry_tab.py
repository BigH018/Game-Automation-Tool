from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QScrollArea, QFrame,
)

from ui.helpers import _hline, _section


class BerryTabMixin:
    """Mixin providing Berry Farming tab builder methods for MainWindow."""

    def _build_tab_berry(self) -> QWidget:
        """Berry Farming tab — status row, key controls, delays, and debug toggle."""
        content = QWidget()
        v = QVBoxLayout(content)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(14)

        v.addWidget(self._build_status_row("berry"))
        v.addWidget(_hline())
        v.addWidget(self._build_berry_key_controls())
        v.addWidget(self._build_berry_delay_controls())
        v.addWidget(self._build_berry_complete_controls())
        v.addStretch()
        v.addWidget(_hline())
        v.addWidget(self._build_berry_size_selector())
        v.addWidget(self._build_berry_mode_selector())
        v.addWidget(self._build_berry_debug_toggle())

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        return scroll

    def _build_berry_key_controls(self) -> QWidget:
        """Game Controls section for the Berry Farming tab."""
        macro = self.core.berry_farming

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Game Controls"))

        # Water Button key row
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        h.addWidget(QLabel("Water Button"))

        self._lbl_berry_water_key = QLabel(macro.water_key.upper())
        self._lbl_berry_water_key.setObjectName("key_value")

        self._btn_berry_water_rebind = QPushButton("Rebind")
        self._btn_berry_water_rebind.setObjectName("btn_rebind")
        self._btn_berry_water_rebind.setProperty("rebinding", "false")
        self._btn_berry_water_rebind.clicked.connect(
            lambda checked=False: self._start_game_key_rebind(
                "water_key", self._lbl_berry_water_key,
                self._btn_berry_water_rebind, self.core.berry_farming
            )
        )

        h.addWidget(self._lbl_berry_water_key)
        h.addStretch()
        h.addWidget(self._btn_berry_water_rebind)
        v.addWidget(row)

        # Repel Button key row
        row2 = QWidget()
        h2 = QHBoxLayout(row2)
        h2.setContentsMargins(0, 0, 0, 0)
        h2.setSpacing(10)

        h2.addWidget(QLabel("Repel Button"))

        self._lbl_berry_repel_key = QLabel(macro.repel_key.upper())
        self._lbl_berry_repel_key.setObjectName("key_value")

        self._btn_berry_repel_rebind = QPushButton("Rebind")
        self._btn_berry_repel_rebind.setObjectName("btn_rebind")
        self._btn_berry_repel_rebind.setProperty("rebinding", "false")
        self._btn_berry_repel_rebind.clicked.connect(
            lambda checked=False: self._start_game_key_rebind(
                "repel_key", self._lbl_berry_repel_key,
                self._btn_berry_repel_rebind, self.core.berry_farming
            )
        )

        h2.addWidget(self._lbl_berry_repel_key)
        h2.addStretch()
        h2.addWidget(self._btn_berry_repel_rebind)
        v.addWidget(row2)

        # Map Button key row — used by Complete Farm to open the town map
        row3 = QWidget()
        h3 = QHBoxLayout(row3)
        h3.setContentsMargins(0, 0, 0, 0)
        h3.setSpacing(10)

        h3.addWidget(QLabel("Map Button"))

        self._lbl_berry_map_key = QLabel(macro.map_key.upper())
        self._lbl_berry_map_key.setObjectName("key_value")

        self._btn_berry_map_rebind = QPushButton("Rebind")
        self._btn_berry_map_rebind.setObjectName("btn_rebind")
        self._btn_berry_map_rebind.setProperty("rebinding", "false")
        self._btn_berry_map_rebind.clicked.connect(
            lambda checked=False: self._start_game_key_rebind(
                "map_key", self._lbl_berry_map_key,
                self._btn_berry_map_rebind, self.core.berry_farming
            )
        )

        h3.addWidget(self._lbl_berry_map_key)
        h3.addStretch()
        h3.addWidget(self._btn_berry_map_rebind)
        v.addWidget(row3)

        # Register in slot registries
        self._slot_key_labels["berry"].append(self._lbl_berry_water_key)
        self._slot_rebind_btns["berry"].append(self._btn_berry_water_rebind)

        return w

    def _build_berry_delay_controls(self) -> QWidget:
        """Delay controls for Berry Farming — shared + pickup-specific."""
        macro = self.core.berry_farming

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Delays — Plant && Water"))

        shared_rows = [
            ("Post-interact delay",  "post_interact_delay",  100, 2000),
            ("Action delay",         "action_delay",         100, 2000),
            ("Move delay",           "move_delay",            50, 1000),
            ("Step hold duration",   "step_hold_duration",    50,  500),
        ]

        for label_text, attr_prefix, range_min, range_max in shared_rows:
            v.addWidget(self._berry_delay_row(macro, label_text, attr_prefix, range_min, range_max))

        v.addSpacing(4)
        v.addWidget(_section("Delays — Pick Up"))

        pickup_rows = [
            ("Pickup delay",  "pickup_delay",  500, 3000),
        ]

        for label_text, attr_prefix, range_min, range_max in pickup_rows:
            v.addWidget(self._berry_delay_row(macro, label_text, attr_prefix, range_min, range_max))

        v.addSpacing(4)
        v.addWidget(_section("Delays — Shrine (Surf)"))

        surf_rows = [
            ("Surf delay",        "surf_delay",        500, 5000),
            ("Surf start delay",  "surf_start_delay",  1000, 10000),
            ("Surf move delay",   "surf_move_delay",   50, 1000),
            ("Surf end delay",    "surf_end_delay",    1000, 10000),
        ]

        for label_text, attr_prefix, range_min, range_max in surf_rows:
            v.addWidget(self._berry_delay_row(macro, label_text, attr_prefix, range_min, range_max))

        return w

    def _berry_delay_row(self, macro, label_text, attr_prefix, range_min, range_max) -> QWidget:
        """Single min/max delay row for berry farming delays."""
        min_attr = f"{attr_prefix}_min"
        max_attr = f"{attr_prefix}_max"

        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        h.addWidget(QLabel(label_text))
        h.addStretch()

        spin_min = QSpinBox()
        spin_min.setRange(range_min, range_max)
        spin_min.setValue(getattr(macro, min_attr))
        spin_min.setFixedWidth(80)
        spin_min.valueChanged.connect(
            lambda val, a=min_attr: setattr(self.core.berry_farming, a, val)
        )

        spin_max = QSpinBox()
        spin_max.setRange(range_min, range_max)
        spin_max.setValue(getattr(macro, max_attr))
        spin_max.setFixedWidth(80)
        spin_max.valueChanged.connect(
            lambda val, a=max_attr: setattr(self.core.berry_farming, a, val)
        )

        self._berry_delay_spins[min_attr] = spin_min
        self._berry_delay_spins[max_attr] = spin_max

        h.addWidget(spin_min)
        h.addWidget(QLabel("ms —"))
        h.addWidget(spin_max)
        h.addWidget(QLabel("ms"))
        return row

    def _build_berry_complete_controls(self) -> QWidget:
        """Complete Farm section — fly location coords and fly delay."""
        macro = self.core.berry_farming

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Complete Farm"))

        # Fly Location row — capture (x, y) via 3-second countdown
        def _coord_display(coords):
            return f"({coords[0]}, {coords[1]})" if coords else "Not set"

        fly_row = QWidget()
        fh = QHBoxLayout(fly_row)
        fh.setContentsMargins(0, 0, 0, 0)
        fh.setSpacing(10)
        fh.addWidget(QLabel("Fly Location"))

        self._lbl_berry_fly_coords = QLabel(_coord_display(macro.fly_coords))
        self._lbl_berry_fly_coords.setObjectName("key_value")

        self._btn_berry_fly_capture = QPushButton("Capture")
        self._btn_berry_fly_capture.setObjectName("btn_rebind")
        self._btn_berry_fly_capture.setProperty("rebinding", "false")
        self._btn_berry_fly_capture.clicked.connect(
            lambda checked=False: self._start_coord_capture(
                "fly_coords", self._lbl_berry_fly_coords,
                self._btn_berry_fly_capture, target=self.core.berry_farming
            )
        )

        fh.addWidget(self._lbl_berry_fly_coords)
        fh.addStretch()
        fh.addWidget(self._btn_berry_fly_capture)
        v.addWidget(fly_row)

        hint = QLabel("Click Capture, hover over the farm on the town map within 3 seconds")
        v.addWidget(hint)

        # Fly delay row — reuses the shared delay-row helper so it lands in _berry_delay_spins
        v.addWidget(self._berry_delay_row(macro, "Fly delay", "fly_delay", 500, 20000))

        return w

    def _build_berry_size_selector(self) -> QWidget:
        """Size selector: Mistralton / Shrine / Single Patch / Complete Farm."""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 2, 0, 2)
        v.setSpacing(6)

        v.addWidget(_section("Size"))

        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        sizes = [
            ("Mistralton",    "full"),
            ("Shrine",        "full2"),
            ("Single Patch",  "single"),
            ("Complete Farm", "complete"),
        ]

        self._berry_size_btns = {}
        for label, size_key in sizes:
            btn = QPushButton(label)
            btn.setObjectName("btn_debug_toggle")
            btn.setProperty("debug_on", "true" if size_key == "full" else "false")
            btn.clicked.connect(lambda checked=False, s=size_key: self._set_berry_size(s))
            h.addWidget(btn)
            self._berry_size_btns[size_key] = btn

        h.addStretch()
        v.addWidget(row)
        return w

    def _set_berry_size(self, size: str):
        """Switch berry farming size and update button highlights."""
        self.core.berry_farming.size = size
        for key, btn in self._berry_size_btns.items():
            btn.setProperty("debug_on", "true" if key == size else "false")
            btn.setStyle(btn.style())

    def _build_berry_mode_selector(self) -> QWidget:
        """Three-button mode selector: Plant & Water, Water Only, Pick Up."""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 2, 0, 2)
        v.setSpacing(6)

        v.addWidget(_section("Mode"))

        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        modes = [
            ("Plant && Water", "plant"),
            ("Water Only",     "water"),
            ("Pick Up",        "pickup"),
        ]

        self._berry_mode_btns = {}
        for label, mode_key in modes:
            btn = QPushButton(label)
            btn.setObjectName("btn_debug_toggle")
            btn.setProperty("debug_on", "true" if mode_key == "plant" else "false")
            btn.clicked.connect(lambda checked=False, m=mode_key: self._set_berry_mode(m))
            h.addWidget(btn)
            self._berry_mode_btns[mode_key] = btn

        h.addStretch()
        v.addWidget(row)

        self._lbl_berry_mode_hint = QLabel("Plant and water each spot (e, e, 4)")
        v.addWidget(self._lbl_berry_mode_hint)

        return w

    def _set_berry_mode(self, mode: str):
        """Switch berry farming mode and update button highlights."""
        self.core.berry_farming.mode = mode
        hints = {
            "plant":  "Plant and water each spot (e, e, 4)",
            "water":  "Skip planting — only water each spot (4)",
            "pickup": "Pick up berries at each spot (e, e)",
        }
        self._lbl_berry_mode_hint.setText(hints[mode])
        for key, btn in self._berry_mode_btns.items():
            btn.setProperty("debug_on", "true" if key == mode else "false")
            btn.setStyle(btn.style())

    def _build_berry_debug_toggle(self) -> QWidget:
        """Debug Mode toggle row at the bottom of the Berry Farming tab."""
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 2, 0, 2)
        h.setSpacing(10)

        self._btn_berry_debug_toggle = QPushButton("Debug Mode")
        self._btn_berry_debug_toggle.setObjectName("btn_debug_toggle")
        self._btn_berry_debug_toggle.setProperty("debug_on", "false")
        self._btn_berry_debug_toggle.clicked.connect(self._toggle_berry_debug_mode)

        hint = QLabel("Logs every key press — never saved to settings")

        h.addWidget(self._btn_berry_debug_toggle)
        h.addWidget(hint)
        h.addStretch()
        return w

    def _toggle_berry_debug_mode(self):
        """Flip debug mode on the Berry Farming macro and update the button appearance."""
        macro = self.core.berry_farming
        macro.debug = not macro.debug
        self._btn_berry_debug_toggle.setProperty(
            "debug_on", "true" if macro.debug else "false"
        )
        self._btn_berry_debug_toggle.setStyle(self._btn_berry_debug_toggle.style())
