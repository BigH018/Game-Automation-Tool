import os, json
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit,
    QFileDialog, QStackedWidget, QScrollArea,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui  import QColor, QPalette, QTextCursor

from ui.core_signals    import CoreSignals
from ui.stylesheet      import (
    C_ACCENT, C_DANGER, C_GOLD,
    DARK, LIGHT, _build_stylesheet,
)
from ui.helpers         import _hline, _section
from ui.guide_window    import GuideWindow

from ui.tabs.settings_tab     import SettingsTabMixin
from ui.tabs.sweet_scent_tab  import SweetScentTabMixin
from ui.tabs.berry_tab        import BerryTabMixin
from ui.tabs.singles_tab      import SinglesTabMixin
from ui.tabs.gtl_tab          import GTLTabMixin
from ui.tabs.gym_run_tab      import GymRunTabMixin
from ui.tabs.trainer_run_tab  import TrainerRunTabMixin
from ui.tabs.fishing_tab      import FishingTabMixin
from ui.tabs.free_shunt_tab   import FreeShuntTabMixin
from ui.tabs.network_tab       import NetworkTabMixin
from ui.tabs.egg_hatching_tab  import EggHatchingTabMixin


class MainWindow(
    QMainWindow,
    SettingsTabMixin,
    SweetScentTabMixin,
    BerryTabMixin,
    SinglesTabMixin,
    GTLTabMixin,
    GymRunTabMixin,
    TrainerRunTabMixin,
    FishingTabMixin,
    FreeShuntTabMixin,
    NetworkTabMixin,
    EggHatchingTabMixin,
):

    def __init__(self, core, hotkey_manager, notification_manager=None,
                 network_listener=None):
        super().__init__()
        self.core    = core
        self.hm      = hotkey_manager
        self.nm      = notification_manager
        self.network_listener = network_listener
        self.signals = CoreSignals()
        self._running     = False
        self._dark        = True
        self._log_entries = []

        # Per-slot widget registries — populated by _build_hotkey_row.
        # Each slot can have multiple key labels and rebind buttons (one per location).
        self._slot_key_labels  = {
            "sweet_scent": [], "berry": [], "singles": [], "gtl": [],
            "gym_run": [], "trainer_run": [], "fishing": [], "free_shunt": [],
            "egg_hatching": [], "kill_switch": [],
        }
        self._slot_rebind_btns = {
            "sweet_scent": [], "berry": [], "singles": [], "gtl": [],
            "gym_run": [], "trainer_run": [], "fishing": [], "free_shunt": [],
            "egg_hatching": [], "kill_switch": [],
        }

        # GTL coordinate-capture state — active while a 3-second countdown is running.
        # Also reused by Berry Farming (Complete Farm fly location).
        self._coord_timer          = None
        self._coord_capture_target = None   # object to setattr on (defaults to gtl_sniper)
        self._coord_capture_attr   = None   # attribute name on target
        self._coord_capture_lbl    = None   # QLabel to update with captured coords
        self._coord_capture_btn    = None   # QPushButton to re-enable after capture
        self._coord_capture_count  = 0

        # Sweet Scent delay spinbox refs — populated by _build_ss_delay_controls.
        # Keys match SweetScentMacro attribute names, e.g. "key_press_delay_min".
        self._ss_delay_spins: dict = {}

        # Berry Farming delay spinbox refs — populated by _build_berry_delay_controls.
        self._berry_delay_spins: dict = {}

        # Singles Farming delay spinbox refs — populated by _build_singles_delay_controls.
        self._singles_delay_spins: dict = {}

        # Game key rebind state — set while a game key rebind is in progress.
        # _game_key_rebind_target: ("sweet_scent" | "singles_farming", attr_name)
        self._game_key_rebinding  = None   # attr name, e.g. "sweet_scent_key" or "a_button_key"
        self._game_key_rebind_lbl = None   # the key display label widget
        self._game_key_rebind_btn = None   # the rebind button widget
        self._game_key_rebind_macro = None # macro object the key belongs to

        self._wire_signals()
        self._build_ui()
        self._apply_style()

    # ── Signal wiring ─────────────────────────────────────────

    def _wire_signals(self):
        """Connect core callbacks → Qt signals → UI slots."""
        self.core.on_log            = lambda msg:   self.signals.log_message.emit(msg)
        self.core.on_start          = lambda:       self.signals.macro_started.emit()
        self.core.on_stop           = lambda:       self.signals.macro_stopped.emit()
        self.core.on_shiny_detected = lambda score: self.signals.shiny_detected.emit(score)

        self.signals.log_message.connect(self._append_log)
        self.signals.macro_started.connect(self._on_started)
        self.signals.macro_stopped.connect(self._on_stopped)
        self.signals.shiny_detected.connect(self._on_shiny)

        self.signals.network_command_result.connect(self._on_network_command_result)

        # rebind_done now emits (slot_name, key_name)
        self.hm.signals.rebind_done.connect(self._on_rebind_done)

    # ── UI construction ───────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("Shiny Hunt Tool - By BigH")
        self.setMinimumSize(520, 640)
        self.resize(660, 860)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        layout.addWidget(self._build_header())
        layout.addWidget(_hline())
        layout.addWidget(self._build_tabs(), stretch=2)
        layout.addWidget(_hline())
        layout.addLayout(self._build_settings_bar())
        layout.addWidget(_hline())
        layout.addLayout(self._build_log_header())
        layout.addWidget(self._build_log(), stretch=1)

        # Populate hint labels now that all status rows exist
        self._update_all_hints()

    # ── Header ────────────────────────────────────────────────

    def _build_header(self) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)

        title = QLabel("✦ SHINY HUNT TOOL")
        title.setStyleSheet(
            f"color: {C_ACCENT}; font-size: 18px; font-weight: bold; letter-spacing: 0.2em;"
        )

        self._lbl_sub = QLabel("by BigH")
        self._lbl_sub.setObjectName("header_sub")
        self._lbl_sub.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        btn_guide = QPushButton("Guide")
        btn_guide.setObjectName("btn_guide")
        btn_guide.setFixedHeight(32)
        btn_guide.setToolTip("Open the guide")
        btn_guide.clicked.connect(self._open_guide)

        self.btn_theme = QPushButton("☀")
        self.btn_theme.setObjectName("btn_theme")
        self.btn_theme.setFixedSize(32, 32)
        self.btn_theme.setToolTip("Toggle light / dark theme")
        self.btn_theme.clicked.connect(self._toggle_theme)

        h.addWidget(title)
        h.addStretch()
        h.addWidget(self._lbl_sub)
        h.addSpacing(8)
        h.addWidget(btn_guide)
        h.addSpacing(4)
        h.addWidget(self.btn_theme)
        return w

    # ── Tab widget ────────────────────────────────────────────

    def _build_tabs(self) -> QWidget:
        wrapper = QWidget()
        vbox = QVBoxLayout(wrapper)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # ── Navigation row: [◀] [scrollable tab buttons] [▶] ──
        nav = QWidget()
        nav_h = QHBoxLayout(nav)
        nav_h.setContentsMargins(0, 0, 0, 0)
        nav_h.setSpacing(4)

        self._btn_tab_left = QPushButton("◀")
        self._btn_tab_left.setObjectName("btn_tab_arrow")
        self._btn_tab_left.setFixedSize(28, 36)
        self._btn_tab_left.clicked.connect(lambda: self._scroll_tab_bar(-1))

        self._btn_tab_right = QPushButton("▶")
        self._btn_tab_right.setObjectName("btn_tab_arrow")
        self._btn_tab_right.setFixedSize(28, 36)
        self._btn_tab_right.clicked.connect(lambda: self._scroll_tab_bar(1))

        # Scrollable button strip
        self._tab_scroll = QScrollArea()
        self._tab_scroll.setObjectName("tab_scroll")
        self._tab_scroll.setWidgetResizable(True)
        self._tab_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._tab_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._tab_scroll.setFixedHeight(40)

        btn_strip = QWidget()
        btn_strip.setObjectName("tab_strip")
        self._tab_btn_layout = QHBoxLayout(btn_strip)
        self._tab_btn_layout.setContentsMargins(0, 0, 0, 0)
        self._tab_btn_layout.setSpacing(2)
        self._tab_scroll.setWidget(btn_strip)

        nav_h.addWidget(self._btn_tab_left)
        nav_h.addWidget(self._tab_scroll, stretch=1)
        nav_h.addWidget(self._btn_tab_right)

        # ── Stacked content area ──
        self._tab_stack = QStackedWidget()
        self._tab_stack.setObjectName("tab_stack")
        self._tab_btns = []

        tab_defs = [
            ("Settings",         self._build_tab_settings()),
            ("Sweet Scent",      self._build_tab_sweet_scent()),
            ("Berry Farming",    self._build_tab_berry()),
            ("Singles Farming",  self._build_tab_singles()),
            ("GTL Sniper",       self._build_tab_gtl()),
            ("Gym Run",          self._build_tab_gym_run()),
            ("Trainer Run",      self._build_tab_trainer_run()),
            ("Fishing",          self._build_tab_fishing()),
            ("Free Shunt",       self._build_tab_free_shunt()),
            ("Egg Hatching",     self._build_tab_egg_hatching()),
            ("Network",          self._build_tab_network()),
        ]

        for idx, (label, page) in enumerate(tab_defs):
            btn = QPushButton(label)
            btn.setObjectName("btn_tab")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self._select_tab(i))
            self._tab_btn_layout.addWidget(btn)
            self._tab_btns.append(btn)
            self._tab_stack.addWidget(page)

        self._select_tab(0)
        self._tab_scroll.horizontalScrollBar().rangeChanged.connect(
            lambda: self._update_tab_arrows()
        )

        vbox.addWidget(nav)
        vbox.addWidget(self._tab_stack, stretch=1)

        return wrapper

    def _select_tab(self, idx: int):
        """Switch to tab at index and update button states."""
        self._tab_stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._tab_btns):
            btn.setChecked(i == idx)
        # Ensure the active button is scrolled into view
        btn = self._tab_btns[idx]
        self._tab_scroll.ensureWidgetVisible(btn, 20, 0)
        self._update_tab_arrows()

    def _scroll_tab_bar(self, direction: int):
        """Scroll the tab button strip left (-1) or right (+1)."""
        sb = self._tab_scroll.horizontalScrollBar()
        sb.setValue(sb.value() + direction * 80)
        self._update_tab_arrows()

    def _update_tab_arrows(self):
        """Enable/disable arrow buttons based on scroll position."""
        sb = self._tab_scroll.horizontalScrollBar()
        self._btn_tab_left.setEnabled(sb.value() > sb.minimum())
        # Before layout, maximum is 0 — fall back to checking total tab count
        if sb.maximum() == 0:
            strip_w = sum(b.sizeHint().width() for b in self._tab_btns)
            strip_w += max(0, len(self._tab_btns) - 1) * 2  # spacing
            can_scroll = strip_w > self._tab_scroll.viewport().width()
            self._btn_tab_right.setEnabled(can_scroll)
        else:
            self._btn_tab_right.setEnabled(sb.value() < sb.maximum())

    # ── Shared tab sub-widgets ────────────────────────────────

    def _build_status_row(self, slot: str) -> QWidget:
        """
        Status indicator row (dot + state label + hint) for a macro tab.
        Widgets are stored as instance attributes named by slot, e.g. lbl_dot_sweet_scent.
        """
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 6, 0, 6)

        dot = QLabel("●")
        dot.setStyleSheet(f"font-size: 22px; color: {C_DANGER};")

        state = QLabel("IDLE")
        state.setStyleSheet(
            f"color: {C_DANGER}; font-size: 15px; font-weight: bold; letter-spacing: 0.22em;"
        )

        hint = QLabel()
        hint.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Store refs by slot name for later updates
        setattr(self, f"lbl_dot_{slot}",   dot)
        setattr(self, f"lbl_state_{slot}", state)
        setattr(self, f"lbl_hint_{slot}",  hint)

        h.addWidget(dot)
        h.addSpacing(10)
        h.addWidget(state)
        h.addStretch()
        h.addWidget(hint)
        return w

    def _build_hotkey_row(self, slot: str, label_text: str) -> QWidget:
        """
        One hotkey display row (label + key name + rebind button).
        Registers the key label and button into the per-slot lists so that all
        instances for the same slot stay in sync when a rebind completes.
        """
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        h.addWidget(QLabel(label_text))

        key_lbl = QLabel(self.hm.key_name(slot))
        key_lbl.setObjectName("key_value")

        btn = QPushButton("Rebind")
        btn.setObjectName("btn_rebind")
        btn.setProperty("rebinding", "false")
        btn.clicked.connect(lambda checked=False, s=slot: self._start_rebind_for(s))

        self._slot_key_labels[slot].append(key_lbl)
        self._slot_rebind_btns[slot].append(btn)

        h.addWidget(key_lbl)
        h.addStretch()
        h.addWidget(btn)
        return w

    # ── Settings bar ──────────────────────────────────────────

    def _build_settings_bar(self) -> QHBoxLayout:
        """Persistent Save / Load row — always visible below the tabs."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self._save_settings)

        btn_load = QPushButton("Load Settings")
        btn_load.clicked.connect(self._load_settings)

        row.addWidget(btn_save)
        row.addWidget(btn_load)
        row.addStretch()
        return row

    # ── Log widgets ───────────────────────────────────────────

    def _build_log_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(_section("Event Log"))
        row.addStretch()
        btn_clear = QPushButton("Clear Log")
        btn_clear.setObjectName("btn_clear")
        btn_clear.clicked.connect(self._clear_log)
        row.addWidget(btn_clear)
        return row

    def _build_log(self) -> QTextEdit:
        self.log = QTextEdit()
        self.log.setObjectName("log")
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(160)
        return self.log

    def _clear_log(self):
        self._log_entries.clear()
        self.log.clear()

    # ── Theme ──────────────────────────────────────────────────

    def _current_colors(self) -> dict:
        return DARK if self._dark else LIGHT

    def _apply_style(self):
        QApplication.instance().setStyle("Fusion")
        c = self._current_colors()

        palette = QPalette()
        palette.setColor(QPalette.Window,          QColor(c["bg"]))
        palette.setColor(QPalette.WindowText,      QColor(c["text"]))
        palette.setColor(QPalette.Base,            QColor(c["surface"]))
        palette.setColor(QPalette.AlternateBase,   QColor(c["dim"]))
        palette.setColor(QPalette.Text,            QColor(c["text"]))
        palette.setColor(QPalette.Button,          QColor(c["surface"]))
        palette.setColor(QPalette.ButtonText,      QColor(c["text"]))
        palette.setColor(QPalette.Highlight,       QColor(C_ACCENT))
        palette.setColor(QPalette.HighlightedText, QColor(c["bg"]))
        QApplication.instance().setPalette(palette)

        self.setStyleSheet(_build_stylesheet(c))

    def _toggle_theme(self):
        self._dark = not self._dark
        self._apply_style()
        self._refresh_dynamic_styles()
        self._rerender_log()
        self.btn_theme.setText("☀" if self._dark else "☾")

    def _refresh_dynamic_styles(self):
        """Re-apply all inline styles that depend on the current theme + state."""
        # Hint labels on each tab
        self._update_all_hints()

        # Refresh all slot status colours to match current running state + theme
        active_slot = None
        if self._running:
            active_slot = self._mode_to_slot(getattr(self.core, "active_mode", None))

        for slot in ("sweet_scent", "berry", "singles", "gtl",
                     "gym_run", "trainer_run", "fishing", "free_shunt",
                     "egg_hatching"):
            state_lbl = getattr(self, f"lbl_state_{slot}", None)
            if slot == active_slot:
                color = C_ACCENT
            elif state_lbl and state_lbl.text() == "SHINY ✦":
                color = C_GOLD
            else:
                color = C_DANGER
            dot   = getattr(self, f"lbl_dot_{slot}",   None)
            state = getattr(self, f"lbl_state_{slot}", None)
            if dot:
                dot.setStyleSheet(f"font-size: 22px; color: {color};")
            if state:
                state.setStyleSheet(
                    f"color: {color}; font-size: 15px; font-weight: bold; letter-spacing: 0.22em;"
                )

    # ── Guide ──────────────────────────────────────────────────

    def _open_guide(self):
        existing = getattr(self, "_guide_window", None)
        if existing is not None and existing.isVisible():
            existing.raise_()
            existing.activateWindow()
        else:
            self._guide_window = GuideWindow(dark=self._dark)
            self._guide_window.show()

    # ── Save / load settings ───────────────────────────────────

    def _save_settings(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Settings", "config.json", "JSON files (*.json)"
        )
        if not path:
            return
        ss  = self.core.sweet_scent
        bf  = self.core.berry_farming
        gtl = self.core.gtl_sniper
        sf  = self.core.singles_farming
        eh  = self.core.egg_hatching
        data = {
            "wav_file":            self.core.wav_file,
            "threshold":           self.core.threshold,
            "device":              self.core.device,
            "samplerate":          self.core.samplerate,
            "hotkey_sweet_scent":   self.hm.key_name("sweet_scent"),
            "hotkey_berry":         self.hm.key_name("berry"),
            "hotkey_singles":       self.hm.key_name("singles"),
            "hotkey_gtl":           self.hm.key_name("gtl"),
            "hotkey_gym_run":       self.hm.key_name("gym_run"),
            "hotkey_trainer_run":   self.hm.key_name("trainer_run"),
            "hotkey_fishing":       self.hm.key_name("fishing"),
            "hotkey_free_shunt":    self.hm.key_name("free_shunt"),
            "hotkey_egg_hatching":  self.hm.key_name("egg_hatching"),
            "hotkey_kill_switch":   self.hm.key_name("kill_switch"),
            "sweet_scent_key":     ss.sweet_scent_key,
            "a_button_key":        ss.a_button_key,
            "sweet_scent": {
                "key_press_delay_min":    ss.key_press_delay_min,
                "key_press_delay_max":    ss.key_press_delay_max,
                "battle_start_delay_min": ss.battle_start_delay_min,
                "battle_start_delay_max": ss.battle_start_delay_max,
                "battle_end_delay_min":   ss.battle_end_delay_min,
                "battle_end_delay_max":   ss.battle_end_delay_max,
            },
            "berry_farming": {
                "water_key":              bf.water_key,
                "repel_key":              bf.repel_key,
                "map_key":                bf.map_key,
                "post_interact_delay_min": bf.post_interact_delay_min,
                "post_interact_delay_max": bf.post_interact_delay_max,
                "action_delay_min":       bf.action_delay_min,
                "action_delay_max":       bf.action_delay_max,
                "move_delay_min":         bf.move_delay_min,
                "move_delay_max":         bf.move_delay_max,
                "step_hold_duration_min": bf.step_hold_duration_min,
                "step_hold_duration_max": bf.step_hold_duration_max,
                "pickup_delay_min":       bf.pickup_delay_min,
                "pickup_delay_max":       bf.pickup_delay_max,
                "surf_delay_min":         bf.surf_delay_min,
                "surf_delay_max":         bf.surf_delay_max,
                "surf_start_delay_min":   bf.surf_start_delay_min,
                "surf_start_delay_max":   bf.surf_start_delay_max,
                "surf_move_delay_min":    bf.surf_move_delay_min,
                "surf_move_delay_max":    bf.surf_move_delay_max,
                "surf_end_delay_min":     bf.surf_end_delay_min,
                "surf_end_delay_max":     bf.surf_end_delay_max,
                "fly_delay_min":          bf.fly_delay_min,
                "fly_delay_max":          bf.fly_delay_max,
                "fly_coords":             list(bf.fly_coords) if bf.fly_coords else None,
            },
            "gtl_sniper": {
                "refresh_coords":  list(gtl.refresh_coords) if gtl.refresh_coords else None,
                "buy_coords":      list(gtl.buy_coords)     if gtl.buy_coords     else None,
                "price_region":    list(gtl.price_region)   if gtl.price_region   else None,
                "max_price":        gtl.max_price,
                "refresh_rate_min": gtl.refresh_rate_min,
                "refresh_rate_max": gtl.refresh_rate_max,
            },
            "singles_farming": {
                "walk_duration_min":      sf.walk_duration_min,
                "walk_duration_max":      sf.walk_duration_max,
                "key_press_delay_min":    sf.key_press_delay_min,
                "key_press_delay_max":    sf.key_press_delay_max,
                "battle_start_delay_min": sf.battle_start_delay_min,
                "battle_start_delay_max": sf.battle_start_delay_max,
                "battle_end_delay_min":   sf.battle_end_delay_min,
                "battle_end_delay_max":   sf.battle_end_delay_max,
                "poll_interval":        sf.poll_interval,
                "hotbar_region":        list(sf.hotbar_region) if sf.hotbar_region else None,
                "a_button_key":         sf.a_button_key,
            },
            "egg_hatching": {
                "grid_top_left":     list(eh.grid_top_left) if eh.grid_top_left else None,
                "grid_bottom_right": list(eh.grid_bottom_right) if eh.grid_bottom_right else None,
                "confirm_coords":    list(eh.confirm_coords) if eh.confirm_coords else None,
                "text_delay_min":    eh.text_delay_min,
                "text_delay_max":    eh.text_delay_max,
                "action_delay_min":  eh.action_delay_min,
                "action_delay_max":  eh.action_delay_max,
                "egg_wait_min":      eh.egg_wait_min,
                "egg_wait_max":      eh.egg_wait_max,
            },
            "discord_notifications_enabled": self.nm.enabled if self.nm else False,
            "network": {
                "listener_port": self._spin_net_listen_port.value(),
                "nodes": [
                    {
                        "ip":   row["ip_edit"].text().strip(),
                        "port": row["port_spin"].value(),
                    }
                    for row in self._net_node_rows
                ],
            },
        }
        # Only save webhook URL if it's not empty
        if self.nm and self.nm.webhook_url:
            data["discord_webhook_url"] = self.nm.webhook_url
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            self._append_log(f"Settings saved to {os.path.basename(path)}")
        except Exception as exc:
            self._append_log(f"Save error: {exc}")

    def _load_settings(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Settings", "", "JSON files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:
            self._append_log(f"Load error: {exc}")
            return

        if not isinstance(data, dict):
            self._append_log("Load error: file does not contain a JSON object.")
            return

        if "wav_file" in data:
            self.edit_wav.setText(str(data["wav_file"]))
        if "threshold" in data:
            self.spin_threshold.setValue(float(data["threshold"]))
        if "device" in data:
            self.spin_device.setValue(int(data["device"]))
        if "samplerate" in data:
            self.spin_sr.setValue(int(data["samplerate"]))

        # Load per-slot hotkeys — also handle old single-key format
        slot_keys = [
            ("sweet_scent",   "hotkey_sweet_scent"),
            ("berry",         "hotkey_berry"),
            ("singles",       "hotkey_singles"),
            ("gtl",           "hotkey_gtl"),
            ("gym_run",       "hotkey_gym_run"),
            ("trainer_run",   "hotkey_trainer_run"),
            ("fishing",       "hotkey_fishing"),
            ("free_shunt",    "hotkey_free_shunt"),
            ("egg_hatching",  "hotkey_egg_hatching"),
            ("kill_switch",   "hotkey_kill_switch"),
        ]
        # Backward compat: old format stored a single "hotkey" for sweet scent
        if "hotkey" in data and "hotkey_sweet_scent" not in data:
            data["hotkey_sweet_scent"] = data["hotkey"]

        for slot, json_key in slot_keys:
            if json_key not in data:
                continue
            key_str = str(data[json_key])
            if self.hm.set_key_by_name(key_str, slot):
                for lbl in self._slot_key_labels[slot]:
                    lbl.setText(self.hm.key_name(slot))
                self._update_slot_hint(slot)
            else:
                self._append_log(f"Unknown hotkey '{key_str}' for {slot} — keeping current key.")

        ss_delays = data.get("sweet_scent", {})
        if isinstance(ss_delays, dict):
            for attr, spin in self._ss_delay_spins.items():
                if attr in ss_delays:
                    spin.setValue(int(ss_delays[attr]))

        if "sweet_scent_key" in data:
            key = str(data["sweet_scent_key"])
            self.core.sweet_scent.sweet_scent_key = key
            self._lbl_ss_key.setText(key.upper())

        if "a_button_key" in data:
            key = str(data["a_button_key"])
            self.core.sweet_scent.a_button_key = key
            self.core.singles_farming.a_button_key = key
            self._lbl_a_button_key.setText(key.upper())

        # Berry Farming settings
        bf_data = data.get("berry_farming", {})
        if isinstance(bf_data, dict):
            bf = self.core.berry_farming

            for attr, spin in self._berry_delay_spins.items():
                if attr in bf_data:
                    spin.setValue(int(bf_data[attr]))

            if "water_key" in bf_data:
                key = str(bf_data["water_key"])
                bf.water_key = key
                self._lbl_berry_water_key.setText(key.upper())

            if "repel_key" in bf_data:
                key = str(bf_data["repel_key"])
                bf.repel_key = key
                self._lbl_berry_repel_key.setText(key.upper())

            if "map_key" in bf_data:
                key = str(bf_data["map_key"])
                bf.map_key = key
                self._lbl_berry_map_key.setText(key.upper())

            fly_val = bf_data.get("fly_coords")
            if isinstance(fly_val, (list, tuple)) and len(fly_val) == 2:
                coords = (int(fly_val[0]), int(fly_val[1]))
                bf.fly_coords = coords
                self._lbl_berry_fly_coords.setText(f"({coords[0]}, {coords[1]})")

        # Discord notification settings
        if self.nm is not None:
            if "discord_webhook_url" in data:
                url = str(data["discord_webhook_url"])
                self.nm.webhook_url = url
                self._edit_webhook.setText(url)
            if "discord_notifications_enabled" in data:
                self.nm.enabled = bool(data["discord_notifications_enabled"])
                on = self.nm.enabled
                self._btn_notif_toggle.setText("Enabled" if on else "Disabled")
                self._btn_notif_toggle.setProperty("notif_on", "true" if on else "false")
                self._btn_notif_toggle.setStyle(self._btn_notif_toggle.style())

        # GTL Sniper settings
        gtl_data = data.get("gtl_sniper", {})
        if isinstance(gtl_data, dict):
            gtl = self.core.gtl_sniper

            def _load_coords(key, lbl):
                val = gtl_data.get(key)
                if isinstance(val, (list, tuple)) and len(val) == 2:
                    coords = (int(val[0]), int(val[1]))
                    setattr(gtl, key, coords)
                    lbl.setText(f"({coords[0]}, {coords[1]})")

            def _load_region(key, lbl):
                val = gtl_data.get(key)
                if isinstance(val, (list, tuple)) and len(val) == 4:
                    region = tuple(int(v) for v in val)
                    setattr(gtl, key, region)
                    lbl.setText(f"({region[0]}, {region[1]})  {region[2]}×{region[3]}")

            _load_coords("refresh_coords", self._lbl_gtl_refresh)
            _load_coords("buy_coords",     self._lbl_gtl_buy)
            _load_region("price_region",   self._lbl_gtl_region)

            if "max_price" in gtl_data:
                gtl.max_price = int(gtl_data["max_price"])
                self._spin_gtl_max_price.setValue(gtl.max_price)
            if "refresh_rate_min" in gtl_data:
                gtl.refresh_rate_min = int(gtl_data["refresh_rate_min"])
                self._spin_gtl_rate_min.setValue(gtl.refresh_rate_min)
            if "refresh_rate_max" in gtl_data:
                gtl.refresh_rate_max = int(gtl_data["refresh_rate_max"])
                self._spin_gtl_rate_max.setValue(gtl.refresh_rate_max)

        # Singles Farming settings
        sf_data = data.get("singles_farming", {})
        if isinstance(sf_data, dict):
            sf = self.core.singles_farming

            for attr, spin in self._singles_delay_spins.items():
                if attr in sf_data:
                    spin.setValue(int(sf_data[attr]))

            if "poll_interval" in sf_data:
                sf.poll_interval = int(sf_data["poll_interval"])
                self._spin_singles_poll.setValue(sf.poll_interval)

            if "hotbar_region" in sf_data:
                val = sf_data["hotbar_region"]
                if isinstance(val, (list, tuple)) and len(val) == 4:
                    region = tuple(int(v) for v in val)
                    sf.hotbar_region = region
                    self._lbl_singles_hotbar_region.setText(
                        f"({region[0]}, {region[1]})  {region[2]}×{region[3]}"
                    )

            if "a_button_key" in sf_data:
                sf.a_button_key = str(sf_data["a_button_key"])

        # Network settings
        net_data = data.get("network", {})
        if isinstance(net_data, dict):
            if "listener_port" in net_data:
                self._spin_net_listen_port.setValue(int(net_data["listener_port"]))
            nodes = net_data.get("nodes", [])
            for i, node in enumerate(nodes):
                if i >= len(self._net_node_rows):
                    break
                if isinstance(node, dict):
                    row = self._net_node_rows[i]
                    if "ip" in node:
                        row["ip_edit"].setText(str(node["ip"]))
                    if "port" in node:
                        row["port_spin"].setValue(int(node["port"]))

        # Egg Hatching settings
        eh_data = data.get("egg_hatching", {})
        if isinstance(eh_data, dict):
            eh = self.core.egg_hatching

            for attr, spin in self._egg_delay_spins.items():
                if attr in eh_data:
                    spin.setValue(int(eh_data[attr]))

            def _load_egg_coords(key, lbl):
                val = eh_data.get(key)
                if isinstance(val, (list, tuple)) and len(val) == 2:
                    coords = (int(val[0]), int(val[1]))
                    setattr(eh, key, coords)
                    lbl.setText(f"({coords[0]}, {coords[1]})")

            _load_egg_coords("grid_top_left",     self._lbl_egg_grid_tl)
            _load_egg_coords("grid_bottom_right",  self._lbl_egg_grid_br)
            _load_egg_coords("confirm_coords",     self._lbl_egg_confirm)

        self._append_log(f"Settings loaded from {os.path.basename(path)}")
        try:
            self.core.start_audio()
        except Exception as exc:
            self._append_log(f"Audio error: {exc}")

    # ── Hotkey hints ──────────────────────────────────────────

    def _update_slot_hint(self, slot: str):
        """Update the hint label on the macro tab for one slot."""
        hint_lbl = getattr(self, f"lbl_hint_{slot}", None)
        if hint_lbl is None:
            return
        key_name = self.hm.key_name(slot)
        hint_lbl.setText(f"{key_name}  start / stop     ESC  quit")

    def _update_all_hints(self):
        """Refresh hint labels on all macro tabs."""
        for slot in ("sweet_scent", "berry", "singles", "gtl",
                     "gym_run", "trainer_run", "fishing", "free_shunt",
                     "egg_hatching"):
            self._update_slot_hint(slot)

    # ── Hotkey rebind ─────────────────────────────────────────

    def _start_rebind_for(self, slot: str):
        """Put ALL hotkey rows for this slot into rebinding mode."""
        for lbl in self._slot_key_labels[slot]:
            lbl.setText("[press a key…]")
        for btn in self._slot_rebind_btns[slot]:
            btn.setText("Cancel")
            btn.setProperty("rebinding", "true")
            btn.setStyle(btn.style())
            btn.clicked.disconnect()
            btn.clicked.connect(lambda checked=False, s=slot: self._cancel_rebind_for(s))
        self.hm.start_rebind(slot)

    def _cancel_rebind_for(self, slot: str):
        self.hm.cancel_rebind()
        self._restore_rebind_row(slot, self.hm.key_name(slot))

    def _on_rebind_done(self, slot: str, key_name: str):
        """Called on Qt thread when pynput completes or ESC-cancels a rebind."""
        if slot == "_game_key":
            self._on_game_key_rebind_done(key_name)
            return
        display = key_name if key_name else self.hm.key_name(slot)
        self._restore_rebind_row(slot, display)
        if key_name:
            self._update_slot_hint(slot)

    def _restore_rebind_row(self, slot: str, key_name: str):
        """Reset ALL hotkey rows for this slot back to normal Rebind state."""
        for lbl in self._slot_key_labels[slot]:
            lbl.setText(key_name)
        for btn in self._slot_rebind_btns[slot]:
            btn.setText("Rebind")
            btn.setProperty("rebinding", "false")
            btn.setStyle(btn.style())
            btn.clicked.disconnect()
            btn.clicked.connect(lambda checked=False, s=slot: self._start_rebind_for(s))

    # ── Game key rebind ───────────────────────────────────────

    def _start_game_key_rebind(self, key_attr: str, lbl, btn,
                               macro=None):
        """Put a game key row into inline rebinding mode, exactly like hotkey rows."""
        self._game_key_rebinding    = key_attr
        self._game_key_rebind_lbl   = lbl
        self._game_key_rebind_btn   = btn
        self._game_key_rebind_macro = macro or self.core.sweet_scent

        lbl.setText("[press a key…]")
        btn.setText("Cancel")
        btn.setProperty("rebinding", "true")
        btn.setStyle(btn.style())
        btn.clicked.disconnect()
        btn.clicked.connect(self._cancel_game_key_rebind)

        # Reuse the HotkeyManager's rebind gate so pynput absorbs the next
        # keypress (including ESC) without routing it as quit or toggle.
        self.hm.start_rebind("_game_key")

    def _cancel_game_key_rebind(self):
        """Cancel the in-progress game key rebind without changing the key."""
        self.hm.cancel_rebind()
        self._finish_game_key_rebind(None)

    def _on_game_key_rebind_done(self, key_name: str):
        """Called from _on_rebind_done when pynput captured a key for a game key row."""
        # key_name is the pynput-formatted key (e.g. "E", "F9") or "" for ESC cancel.
        # interception-python uses lowercase strings (e.g. "e", "f9").
        self._finish_game_key_rebind(key_name.lower() if key_name else None)

    def _finish_game_key_rebind(self, new_key):
        """Apply the captured key (or None to cancel) and restore the row."""
        key_attr = self._game_key_rebinding
        lbl      = self._game_key_rebind_lbl
        btn      = self._game_key_rebind_btn
        macro    = self._game_key_rebind_macro or self.core.sweet_scent

        if new_key is not None:
            setattr(macro, key_attr, new_key)
            # A button key is shared between Sweet Scent and Singles Farming
            if key_attr == "a_button_key":
                for m in (self.core.sweet_scent, self.core.singles_farming):
                    setattr(m, key_attr, new_key)
                # Sync the A-button display label
                self._lbl_a_button_key.setText(new_key.upper())

        display = getattr(macro, key_attr).upper()
        lbl.setText(display)

        btn.setText("Rebind")
        btn.setProperty("rebinding", "false")
        btn.setStyle(btn.style())
        btn.clicked.disconnect()
        btn.clicked.connect(
            lambda checked=False, a=key_attr, l=lbl, b=btn, m=macro:
                self._start_game_key_rebind(a, l, b, m)
        )

        self._game_key_rebinding    = None
        self._game_key_rebind_lbl   = None
        self._game_key_rebind_btn   = None
        self._game_key_rebind_macro = None

    # ── Slots ─────────────────────────────────────────────────

    def _browse_wav(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select WAV file", "", "WAV files (*.wav)"
        )
        if path:
            self.edit_wav.setText(path)
            try:
                self.core.start_audio()
            except Exception as exc:
                self.signals.log_message.emit(f"Audio error: {exc}")

    def _mode_to_slot(self, mode: str) -> str:
        return {
            "sweet_scent":     "sweet_scent",
            "berry_farming":   "berry",
            "singles_farming": "singles",
            "gtl_sniper":      "gtl",
            "gym_run":         "gym_run",
            "trainer_run":     "trainer_run",
            "fishing":         "fishing",
            "free_shunt":      "free_shunt",
            "egg_hatching":    "egg_hatching",
        }.get(mode or "", "sweet_scent")

    def _set_slot_status(self, slot: str, color: str, text: str):
        dot   = getattr(self, f"lbl_dot_{slot}",   None)
        state = getattr(self, f"lbl_state_{slot}", None)
        if dot:
            dot.setStyleSheet(f"font-size: 22px; color: {color};")
        if state:
            state.setStyleSheet(
                f"color: {color}; font-size: 15px; font-weight: bold; letter-spacing: 0.22em;"
            )
            state.setText(text)

    def _on_started(self):
        self._running = True
        slot = self._mode_to_slot(getattr(self.core, "active_mode", None))
        self._set_slot_status(slot, C_ACCENT, "RUNNING")

    def _on_stopped(self):
        self._running = False
        slot = self._mode_to_slot(getattr(self.core, "active_mode", None))
        self._set_slot_status(slot, C_DANGER, "IDLE")

    def _on_shiny(self, score: float):
        """Flash the active macro's status gold when a shiny is detected."""
        slot = self._mode_to_slot(getattr(self.core, "active_mode", None))
        self._set_slot_status(slot, C_GOLD, "SHINY ✦")

    def _append_log(self, message: str):
        ts = datetime.now().strftime("%H:%M:%S")

        if "SHINY" in message:
            color_type = "gold"
        elif "stopped" in message.lower():
            color_type = "danger"
        elif "started" in message.lower() or "active" in message.lower():
            color_type = "accent"
        else:
            color_type = "default"

        self._log_entries.append((ts, message, color_type))
        self._render_log_entry(ts, message, color_type)

    def _render_log_entry(self, ts: str, message: str, color_type: str):
        c = self._current_colors()
        color_map = {
            "gold":    C_GOLD,
            "danger":  C_DANGER,
            "accent":  C_ACCENT,
            "default": c["text"],
        }
        color = color_map[color_type]

        safe_msg = (
            message.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
        )
        html = (
            f'<span style="color:{c["muted"]};">{ts}</span> '
            f'<span style="color:{color};">{safe_msg}</span>'
        )
        self.log.append(html)
        self.log.moveCursor(QTextCursor.End)

    def _rerender_log(self):
        """Rebuild the log with current theme colours."""
        self.log.clear()
        for ts, message, color_type in self._log_entries:
            self._render_log_entry(ts, message, color_type)
