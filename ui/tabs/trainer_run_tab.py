from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from ui.helpers import _hline


class TrainerRunTabMixin:
    """Mixin providing Trainer Run tab builder methods for MainWindow."""

    def _build_tab_trainer_run(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(14)

        v.addWidget(self._build_status_row("trainer_run"))
        v.addWidget(_hline())

        lbl = QLabel("Trainer Run controls will appear here.")
        lbl.setObjectName("tab_placeholder")
        v.addWidget(lbl)
        v.addStretch()
        return w
