from PyQt5.QtCore import pyqtSignal, QObject


class CoreSignals(QObject):
    """Emitted from background threads; connected to Qt slots in the UI."""
    log_message    = pyqtSignal(str)
    macro_started  = pyqtSignal()
    macro_stopped  = pyqtSignal()
    shiny_detected = pyqtSignal(float)

    # ── Network ──
    network_command        = pyqtSignal(str)          # command from remote listener
    network_command_result = pyqtSignal(str, bool)    # (node_label, success)
