from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from ui.helpers import _hline


class GymRunTabMixin:
    """Mixin providing Gym Run tab builder methods for MainWindow."""

    def _build_tab_gym_run(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(14)

        v.addWidget(self._build_status_row("gym_run"))
        v.addWidget(_hline())

        lbl = QLabel("Gym Run controls will appear here.")
        lbl.setObjectName("tab_placeholder")
        v.addWidget(lbl)
        v.addStretch()
        return w
