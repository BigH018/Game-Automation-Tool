from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QScrollArea, QFrame,
)

from ui.helpers import _hline, _section


class EggHatchingTabMixin:
    """Mixin providing Egg Hatching tab builder methods for MainWindow."""

    def _build_tab_egg_hatching(self) -> QWidget:
        """Egg Hatching tab — grid setup, click target, delays, debug toggle."""
        content = QWidget()
        v = QVBoxLayout(content)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(14)

        v.addWidget(self._build_status_row("egg_hatching"))
        v.addWidget(_hline())
        v.addWidget(self._build_egg_grid_setup())
        v.addWidget(self._build_egg_click_target())
        v.addWidget(self._build_egg_delay_controls())
        v.addStretch()
        v.addWidget(_hline())
        v.addWidget(self._build_egg_debug_toggle())

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        return scroll

    # ── Grid Setup ────────────────────────────────────────────

    def _build_egg_grid_setup(self) -> QWidget:
        """Grid reference points — top-left (R1C1) and bottom-right (R6C10)."""
        macro = self.core.egg_hatching

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Grid Setup (6 rows × 10 columns)"))

        def _coord_display(coords):
            return f"({coords[0]}, {coords[1]})" if coords else "Not set"

        # Top-Left Cell (R1 C1)
        tl_row = QWidget()
        tlh = QHBoxLayout(tl_row)
        tlh.setContentsMargins(0, 0, 0, 0)
        tlh.setSpacing(10)
        tlh.addWidget(QLabel("Top-Left Cell (R1 C1)"))

        self._lbl_egg_grid_tl = QLabel(_coord_display(macro.grid_top_left))
        self._lbl_egg_grid_tl.setObjectName("key_value")

        self._btn_egg_grid_tl = QPushButton("Capture")
        self._btn_egg_grid_tl.setObjectName("btn_rebind")
        self._btn_egg_grid_tl.setProperty("rebinding", "false")
        self._btn_egg_grid_tl.clicked.connect(
            lambda checked=False: self._start_coord_capture(
                "grid_top_left", self._lbl_egg_grid_tl,
                self._btn_egg_grid_tl, target=self.core.egg_hatching
            )
        )

        tlh.addWidget(self._lbl_egg_grid_tl)
        tlh.addStretch()
        tlh.addWidget(self._btn_egg_grid_tl)
        v.addWidget(tl_row)

        # Bottom-Right Cell (R6 C10)
        br_row = QWidget()
        brh = QHBoxLayout(br_row)
        brh.setContentsMargins(0, 0, 0, 0)
        brh.setSpacing(10)
        brh.addWidget(QLabel("Bottom-Right Cell (R6 C10)"))

        self._lbl_egg_grid_br = QLabel(_coord_display(macro.grid_bottom_right))
        self._lbl_egg_grid_br.setObjectName("key_value")

        self._btn_egg_grid_br = QPushButton("Capture")
        self._btn_egg_grid_br.setObjectName("btn_rebind")
        self._btn_egg_grid_br.setProperty("rebinding", "false")
        self._btn_egg_grid_br.clicked.connect(
            lambda checked=False: self._start_coord_capture(
                "grid_bottom_right", self._lbl_egg_grid_br,
                self._btn_egg_grid_br, target=self.core.egg_hatching
            )
        )

        brh.addWidget(self._lbl_egg_grid_br)
        brh.addStretch()
        brh.addWidget(self._btn_egg_grid_br)
        v.addWidget(br_row)

        hint = QLabel(
            "Capture the centre of the top-left cell (R1 C1) and "
            "bottom-right cell (R6 C10). All 60 cells are calculated from these two points."
        )
        hint.setWordWrap(True)
        v.addWidget(hint)

        return w

    # ── Click Target ──────────────────────────────────────────

    def _build_egg_click_target(self) -> QWidget:
        """Fixed confirm-click target captured via the shared coord capture flow."""
        macro = self.core.egg_hatching

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Click Target"))

        def _coord_display(coords):
            return f"({coords[0]}, {coords[1]})" if coords else "Not set"

        row = QWidget()
        rh = QHBoxLayout(row)
        rh.setContentsMargins(0, 0, 0, 0)
        rh.setSpacing(10)
        rh.addWidget(QLabel("Confirm Click"))

        self._lbl_egg_confirm = QLabel(_coord_display(macro.confirm_coords))
        self._lbl_egg_confirm.setObjectName("key_value")

        self._btn_egg_confirm = QPushButton("Capture")
        self._btn_egg_confirm.setObjectName("btn_rebind")
        self._btn_egg_confirm.setProperty("rebinding", "false")
        self._btn_egg_confirm.clicked.connect(
            lambda checked=False: self._start_coord_capture(
                "confirm_coords", self._lbl_egg_confirm,
                self._btn_egg_confirm, target=self.core.egg_hatching
            )
        )

        rh.addWidget(self._lbl_egg_confirm)
        rh.addStretch()
        rh.addWidget(self._btn_egg_confirm)
        v.addWidget(row)

        hint = QLabel("The normal left-click target after selecting both grid slots each iteration.")
        hint.setWordWrap(True)
        v.addWidget(hint)

        return w

    # ── Delays ────────────────────────────────────────────────

    def _build_egg_delay_controls(self) -> QWidget:
        """Min/max delay controls for the egg hatching macro."""
        macro = self.core.egg_hatching

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Delays"))

        rows = [
            ("Text delay",      "text_delay",   100, 5000),
            ("Action delay",    "action_delay",  50, 2000),
            ("Wait for egg",    "egg_wait",      50, 3000),
        ]

        self._egg_delay_spins: dict = {}

        for label_text, attr_prefix, range_min, range_max in rows:
            v.addWidget(self._egg_delay_row(macro, label_text, attr_prefix, range_min, range_max))

        hint = QLabel("Randomised delays between each action to avoid pattern detection.")
        hint.setWordWrap(True)
        v.addWidget(hint)

        return w

    def _egg_delay_row(self, macro, label_text, attr_prefix, range_min, range_max) -> QWidget:
        """Single min/max delay row for egg hatching delays."""
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
            lambda val, a=min_attr: setattr(self.core.egg_hatching, a, val)
        )

        spin_max = QSpinBox()
        spin_max.setRange(range_min, range_max)
        spin_max.setValue(getattr(macro, max_attr))
        spin_max.setFixedWidth(80)
        spin_max.valueChanged.connect(
            lambda val, a=max_attr: setattr(self.core.egg_hatching, a, val)
        )

        self._egg_delay_spins[min_attr] = spin_min
        self._egg_delay_spins[max_attr] = spin_max

        h.addWidget(spin_min)
        h.addWidget(QLabel("ms —"))
        h.addWidget(spin_max)
        h.addWidget(QLabel("ms"))
        return row

    # ── Debug toggle ──────────────────────────────────────────

    def _build_egg_debug_toggle(self) -> QWidget:
        """Debug Mode toggle row at the bottom of the Egg Hatching tab."""
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 2, 0, 2)
        h.setSpacing(10)

        self._btn_egg_debug_toggle = QPushButton("Debug Mode")
        self._btn_egg_debug_toggle.setObjectName("btn_debug_toggle")
        self._btn_egg_debug_toggle.setProperty("debug_on", "false")
        self._btn_egg_debug_toggle.clicked.connect(self._toggle_egg_debug_mode)

        hint = QLabel("Logs every action and grid coordinate — never saved to settings")

        h.addWidget(self._btn_egg_debug_toggle)
        h.addWidget(hint)
        h.addStretch()
        return w

    def _toggle_egg_debug_mode(self):
        """Flip debug mode on the Egg Hatching macro and update the button appearance."""
        macro = self.core.egg_hatching
        macro.debug = not macro.debug
        self._btn_egg_debug_toggle.setProperty(
            "debug_on", "true" if macro.debug else "false"
        )
        self._btn_egg_debug_toggle.setStyle(self._btn_egg_debug_toggle.style())
