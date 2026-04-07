from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QScrollArea, QFrame,
)

from ui.helpers          import _hline, _section
from ui.region_selector  import RegionSelector


class SinglesTabMixin:
    """Mixin providing Singles Farming tab builder methods for MainWindow."""

    def _build_tab_singles(self) -> QWidget:
        """Singles Farming tab — status row, key controls, region, delays, debug."""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(14)

        v.addWidget(self._build_status_row("singles"))
        v.addWidget(_hline())
        v.addWidget(self._build_singles_hotbar_region())
        v.addWidget(self._build_singles_delay_controls())

        # Poll Interval
        v.addWidget(_section("Detection"))
        poll_row = QWidget()
        ph = QHBoxLayout(poll_row)
        ph.setContentsMargins(0, 0, 0, 0)
        ph.setSpacing(8)
        ph.addWidget(QLabel("Poll interval"))
        ph.addStretch()
        spin_poll = QSpinBox()
        spin_poll.setRange(10, 1000)
        spin_poll.setSingleStep(10)
        spin_poll.setValue(self.core.singles_farming.poll_interval)
        spin_poll.setFixedWidth(80)
        spin_poll.valueChanged.connect(
            lambda val: setattr(self.core.singles_farming, "poll_interval", val)
        )
        self._spin_singles_poll = spin_poll
        ph.addWidget(spin_poll)
        ph.addWidget(QLabel("ms"))
        v.addWidget(poll_row)

        v.addStretch()
        v.addWidget(_hline())
        v.addWidget(self._build_singles_debug_toggle())

        scroll = QScrollArea()
        scroll.setWidget(w)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        return scroll

    def _build_singles_hotbar_region(self) -> QWidget:
        """Hotbar Region section — label + Set Region button."""
        macro = self.core.singles_farming

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Hotbar Region"))

        region_row = QWidget()
        rh = QHBoxLayout(region_row)
        rh.setContentsMargins(0, 0, 0, 0)
        rh.setSpacing(10)
        rh.addWidget(QLabel("Hotbar Region"))

        def _region_display(r):
            return f"({r[0]}, {r[1]})  {r[2]}×{r[3]}" if r else "Not set"

        self._lbl_singles_hotbar_region = QLabel(_region_display(macro.hotbar_region))
        self._lbl_singles_hotbar_region.setObjectName("key_value")

        self._btn_singles_set_region = QPushButton("Set Region")
        self._btn_singles_set_region.setObjectName("btn_rebind")
        self._btn_singles_set_region.clicked.connect(self._open_singles_region_selector)

        rh.addWidget(self._lbl_singles_hotbar_region)
        rh.addStretch()
        rh.addWidget(self._btn_singles_set_region)
        v.addWidget(region_row)

        hint = QLabel("Click and drag over the hotbar area; ESC to cancel")
        hint.setStyleSheet("font-size: 10px;")
        v.addWidget(hint)

        return w

    def _build_singles_delay_controls(self) -> QWidget:
        """Walk duration and battle-end delay pairs for Singles Farming."""
        macro = self.core.singles_farming

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Delays"))

        delay_rows = [
            ("Walk duration",      "walk_duration",      50,  5000),
            ("Key press delay",    "key_press_delay",    0,   99999),
            ("Battle start delay", "battle_start_delay", 500, 15000),
            ("Battle end delay",   "battle_end_delay",   500, 15000),
        ]

        for label_text, attr_prefix, range_min, range_max in delay_rows:
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
                lambda val, a=min_attr: setattr(self.core.singles_farming, a, val)
            )

            spin_max = QSpinBox()
            spin_max.setRange(range_min, range_max)
            spin_max.setValue(getattr(macro, max_attr))
            spin_max.setFixedWidth(80)
            spin_max.valueChanged.connect(
                lambda val, a=max_attr: setattr(self.core.singles_farming, a, val)
            )

            self._singles_delay_spins[min_attr] = spin_min
            self._singles_delay_spins[max_attr] = spin_max

            h.addWidget(spin_min)
            h.addWidget(QLabel("ms —"))
            h.addWidget(spin_max)
            h.addWidget(QLabel("ms"))
            v.addWidget(row)

        return w

    def _build_singles_debug_toggle(self) -> QWidget:
        """Debug Mode toggle row at the bottom of the Singles Farming tab."""
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 2, 0, 2)
        h.setSpacing(10)

        self._btn_singles_debug_toggle = QPushButton("Debug Mode")
        self._btn_singles_debug_toggle.setObjectName("btn_debug_toggle")
        self._btn_singles_debug_toggle.setProperty("debug_on", "false")
        self._btn_singles_debug_toggle.clicked.connect(self._toggle_singles_debug_mode)

        h.addWidget(self._btn_singles_debug_toggle)
        h.addStretch()
        return w

    def _toggle_singles_debug_mode(self):
        """Flip debug mode on the Singles Farming macro and update the button appearance."""
        macro = self.core.singles_farming
        macro.debug = not macro.debug
        self._btn_singles_debug_toggle.setProperty("debug_on", "true" if macro.debug else "false")
        self._btn_singles_debug_toggle.setStyle(self._btn_singles_debug_toggle.style())

    def _open_singles_region_selector(self):
        """Show the fullscreen drag-to-select overlay for the hotbar region."""
        self._singles_region_selector = RegionSelector()
        self._singles_region_selector.region_selected.connect(self._on_singles_region_selected)
        self._singles_region_selector.cancelled.connect(
            lambda: self._append_log("Hotbar region selection cancelled.")
        )
        self._singles_region_selector.show()
        self._singles_region_selector.activateWindow()
        self._singles_region_selector.raise_()

    def _on_singles_region_selected(self, x: int, y: int, w: int, h: int):
        self.core.singles_farming.hotbar_region = (x, y, w, h)
        self._lbl_singles_hotbar_region.setText(f"({x}, {y})  {w}×{h}")
        self._append_log(f"Hotbar region set: ({x}, {y})  {w}×{h} px")
