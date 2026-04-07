# Re-export shim — keeps `from ui import MainWindow` working for main.py
from ui.main_window import MainWindow

__all__ = ["MainWindow"]
