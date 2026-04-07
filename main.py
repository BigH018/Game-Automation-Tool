"""
main.py — Entry point for Shiny Hunt Tool - By BigH.

Start with:
    python main.py

Hotkeys (global, work even when window is not focused):
    F9   — Start / Stop Sweet Scent macro (default, rebindable)
    F8   — Start / Stop Berry Farming macro (default, rebindable)
    F7   — Start / Stop Singles Farming macro (default, rebindable)
    F6   — Start / Stop GTL Sniper macro (default, rebindable)
    F5   — Start / Stop Gym Run macro (default, rebindable)
    F4   — Start / Stop Trainer Run macro (default, rebindable)
    F3   — Start / Stop Fishing macro (default, rebindable)
    F2   — Start / Stop Free Shunt macro (default, rebindable)
    F1   — Start / Stop Egg Hatching macro (default, rebindable)
    F10  — Kill switch / quit (default, rebindable)
"""

import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from core             import MacroCore
from ui               import MainWindow
from hotkeys          import HotkeyManager
from notifications    import NotificationManager
from network_listener import NetworkListener


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("BH-Tools")

    core = MacroCore()
    nm   = NotificationManager()
    nl   = NetworkListener()

    # Let the notification manager log through core's log callback chain
    nm.on_log = lambda msg: core._log(msg)
    core.notification_manager = nm
    nm.check_available()

    # Wire network listener callbacks through core's log chain
    nl.on_log = lambda msg: core._log(msg)

    try:
        core.start_audio()
    except Exception as exc:
        QMessageBox.critical(
            None, "Audio Error",
            f"Could not start audio listener:\n{exc}\n\n"
            "Check that the WAV file exists and the device index is correct."
        )

    hm = HotkeyManager()

    window = MainWindow(core, hm, nm, network_listener=nl)
    window.show()

    # Route network listener commands to the Qt main thread via signal
    nl.on_command = lambda cmd: window.signals.network_command.emit(cmd)

    def _handle_network_command(cmd: str):
        if cmd == "stop":
            core.stop()
        elif cmd.startswith("start:"):
            mode = cmd.split(":", 1)[1]
            if not core.running:
                core.start(mode)

    window.signals.network_command.connect(_handle_network_command)

    # Wire hotkey signals → core and app (on Qt main thread via signal/slot)
    def _make_toggle(mode: str):
        def _toggle():
            if core.running:
                core.stop()
            else:
                core.start(mode)
        return _toggle

    def _on_quit():
        nl.stop_listening()
        core.stop()
        app.quit()

    hm.signals.toggle.connect(_make_toggle("sweet_scent"))
    hm.signals.toggle_berry.connect(_make_toggle("berry_farming"))
    hm.signals.toggle_singles.connect(_make_toggle("singles_farming"))
    hm.signals.toggle_gtl.connect(_make_toggle("gtl_sniper"))
    hm.signals.toggle_gym_run.connect(_make_toggle("gym_run"))
    hm.signals.toggle_trainer_run.connect(_make_toggle("trainer_run"))
    hm.signals.toggle_fishing.connect(_make_toggle("fishing"))
    hm.signals.toggle_free_shunt.connect(_make_toggle("free_shunt"))
    hm.signals.toggle_egg_hatching.connect(_make_toggle("egg_hatching"))
    hm.signals.quit.connect(_on_quit)

    hm.start()

    exit_code = app.exec_()
    hm.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
