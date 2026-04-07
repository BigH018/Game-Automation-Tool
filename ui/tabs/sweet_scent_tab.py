from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox,
)

from ui.helpers import _hline, _section


class SweetScentTabMixin:
    """Mixin providing Sweet Scent tab builder methods for MainWindow."""

    def _build_tab_sweet_scent(self) -> QWidget:
        """Sweet Scent tab — status row, key controls, and delay controls."""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(14)

        v.addWidget(self._build_status_row("sweet_scent"))
        v.addWidget(_hline())
        v.addWidget(self._build_ss_key_controls())
        v.addWidget(self._build_ss_delay_controls())
        v.addStretch()
        v.addWidget(_hline())
        v.addWidget(self._build_debug_toggle())
        return w

    def _build_ss_delay_controls(self) -> QWidget:
        """Three min/max delay pairs for the Sweet Scent macro."""
        macro = self.core.sweet_scent

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Delays"))

        delay_rows = [
            ("Key press delay",    "key_press_delay"),
            ("Battle start delay", "battle_start_delay"),
            ("Battle end delay",   "battle_end_delay"),
        ]

        for label_text, attr_prefix in delay_rows:
            min_attr = f"{attr_prefix}_min"
            max_attr = f"{attr_prefix}_max"

            row = QWidget()
            h = QHBoxLayout(row)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(8)

            h.addWidget(QLabel(label_text))
            h.addStretch()

            spin_min = QSpinBox()
            spin_min.setRange(0, 99999)
            spin_min.setValue(getattr(macro, min_attr))
            spin_min.setFixedWidth(80)
            spin_min.valueChanged.connect(
                lambda val, a=min_attr: setattr(self.core.sweet_scent, a, val)
            )

            spin_max = QSpinBox()
            spin_max.setRange(0, 99999)
            spin_max.setValue(getattr(macro, max_attr))
            spin_max.setFixedWidth(80)
            spin_max.valueChanged.connect(
                lambda val, a=max_attr: setattr(self.core.sweet_scent, a, val)
            )

            self._ss_delay_spins[min_attr] = spin_min
            self._ss_delay_spins[max_attr] = spin_max

            h.addWidget(spin_min)
            h.addWidget(QLabel("ms —"))
            h.addWidget(spin_max)
            h.addWidget(QLabel("ms"))
            v.addWidget(row)

        return w

    def _build_ss_key_controls(self) -> QWidget:
        """Sweet Scent Button rebind row for the Sweet Scent tab."""
        macro = self.core.sweet_scent

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Controls"))

        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        h.addWidget(QLabel("Sweet Scent Button"))

        self._lbl_ss_key = QLabel(macro.sweet_scent_key.upper())
        self._lbl_ss_key.setObjectName("key_value")

        self._btn_ss_rebind = QPushButton("Rebind")
        self._btn_ss_rebind.setObjectName("btn_rebind")
        self._btn_ss_rebind.setProperty("rebinding", "false")
        self._btn_ss_rebind.clicked.connect(
            lambda checked=False: self._start_game_key_rebind(
                "sweet_scent_key", self._lbl_ss_key, self._btn_ss_rebind
            )
        )

        h.addWidget(self._lbl_ss_key)
        h.addStretch()
        h.addWidget(self._btn_ss_rebind)
        v.addWidget(row)

        return w

    def _build_debug_toggle(self) -> QWidget:
        """Debug Mode toggle row at the bottom of the Sweet Scent tab."""
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 2, 0, 2)
        h.setSpacing(10)

        self._btn_debug_toggle = QPushButton("Debug Mode")
        self._btn_debug_toggle.setObjectName("btn_debug_toggle")
        self._btn_debug_toggle.setProperty("debug_on", "false")
        self._btn_debug_toggle.clicked.connect(self._toggle_debug_mode)

        h.addWidget(self._btn_debug_toggle)
        h.addStretch()
        return w

    def _toggle_debug_mode(self):
        """Flip debug mode on the Sweet Scent macro and update the button appearance."""
        macro = self.core.sweet_scent
        macro.debug = not macro.debug
        self._btn_debug_toggle.setProperty("debug_on", "true" if macro.debug else "false")
        self._btn_debug_toggle.setStyle(self._btn_debug_toggle.style())
