import socket
import threading

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QLineEdit, QScrollArea, QFrame,
)

from ui.helpers    import _hline, _section
from ui.stylesheet import C_ACCENT, C_DANGER
from network_controller import NetworkController


class NetworkTabMixin:
    """Mixin providing Network tab builder methods for MainWindow."""

    def _build_tab_network(self) -> QWidget:
        """Network tab — listener controls, remote node controllers."""
        content = QWidget()
        v = QVBoxLayout(content)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(14)

        v.addWidget(self._build_network_listener_section())
        v.addWidget(_hline())
        v.addWidget(self._build_network_controller_section())
        v.addWidget(_hline())

        hint1 = QLabel("Commands received by this machine are shown in the main event log.")
        v.addWidget(hint1)

        hint2 = QLabel(
            "To allow connections on Windows run as admin: "
            "netsh advfirewall firewall add rule name=BH-Tools-Listener "
            "dir=in action=allow protocol=TCP localport=6789"
        )
        v.addWidget(hint2)

        v.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        return scroll

    # ── Listener section ─────────────────────────────────────

    def _build_network_listener_section(self) -> QWidget:
        """This machine as a farm node — port, start/stop, status, local IP."""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Listener"))

        # Port row
        port_row = QWidget()
        ph = QHBoxLayout(port_row)
        ph.setContentsMargins(0, 0, 0, 0)
        ph.setSpacing(10)
        ph.addWidget(QLabel("Port"))

        self._spin_net_listen_port = QSpinBox()
        self._spin_net_listen_port.setRange(1024, 65535)
        self._spin_net_listen_port.setValue(self.network_listener.port)
        self._spin_net_listen_port.setFixedWidth(90)
        self._spin_net_listen_port.valueChanged.connect(
            lambda val: setattr(self.network_listener, "port", val)
        )

        ph.addWidget(self._spin_net_listen_port)
        ph.addStretch()
        v.addWidget(port_row)

        # Start/Stop + Status row
        ctrl_row = QWidget()
        ch = QHBoxLayout(ctrl_row)
        ch.setContentsMargins(0, 0, 0, 0)
        ch.setSpacing(10)

        self._btn_net_listen_toggle = QPushButton("Start Listener")
        self._btn_net_listen_toggle.clicked.connect(self._toggle_network_listener)

        self._lbl_net_listen_status = QLabel("OFFLINE")
        self._lbl_net_listen_status.setStyleSheet(
            f"color: {C_DANGER}; font-size: 12px; font-weight: bold; letter-spacing: 0.14em;"
        )

        ch.addWidget(self._btn_net_listen_toggle)
        ch.addSpacing(10)
        ch.addWidget(self._lbl_net_listen_status)
        ch.addStretch()
        v.addWidget(ctrl_row)

        # Local IP row
        ip_row = QWidget()
        ih = QHBoxLayout(ip_row)
        ih.setContentsMargins(0, 0, 0, 0)
        ih.setSpacing(10)
        ih.addWidget(QLabel("Local IP"))

        self._lbl_net_local_ip = QLabel("—")
        self._lbl_net_local_ip.setObjectName("key_value")

        btn_detect = QPushButton("Detect")
        btn_detect.setObjectName("btn_scan")
        btn_detect.clicked.connect(self._detect_local_ip)

        ih.addWidget(self._lbl_net_local_ip)
        ih.addStretch()
        ih.addWidget(btn_detect)
        v.addWidget(ip_row)

        return w

    def _toggle_network_listener(self):
        """Start or stop the network listener."""
        if self.network_listener.running:
            self.network_listener.stop_listening()
            self._btn_net_listen_toggle.setText("Start Listener")
            self._btn_net_listen_toggle.setStyleSheet("")
            self._lbl_net_listen_status.setText("OFFLINE")
            self._lbl_net_listen_status.setStyleSheet(
                f"color: {C_DANGER}; font-size: 12px; font-weight: bold; letter-spacing: 0.14em;"
            )
        else:
            self.network_listener.port = self._spin_net_listen_port.value()
            try:
                self.network_listener.start_listening()
            except Exception as exc:
                self.signals.log_message.emit(f"Network listener error: {exc}")
                return
            self._btn_net_listen_toggle.setText("Stop Listener")
            self._btn_net_listen_toggle.setStyleSheet(
                f"border-color: {C_ACCENT}; color: {C_ACCENT};"
            )
            self._lbl_net_listen_status.setText("LISTENING")
            self._lbl_net_listen_status.setStyleSheet(
                f"color: {C_ACCENT}; font-size: 12px; font-weight: bold; letter-spacing: 0.14em;"
            )

    def _detect_local_ip(self):
        """Resolve local IP via socket and display it."""
        try:
            ip = socket.gethostbyname(socket.gethostname())
            self._lbl_net_local_ip.setText(ip)
        except Exception:
            self._lbl_net_local_ip.setText("unknown")

    # ── Controller section ───────────────────────────────────

    def _build_network_controller_section(self) -> QWidget:
        """Send commands to remote farm nodes — 4 node rows."""
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        v.addWidget(_section("Controller"))

        self._net_node_rows = []

        for i in range(4):
            node_label = f"Node {i + 1}"
            row_widgets = self._build_node_row(node_label, i)
            v.addWidget(row_widgets)

        return w

    def _build_node_row(self, node_label: str, index: int) -> QWidget:
        """Single remote node row — label, IP, port, mode buttons, stop, status."""
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        lbl = QLabel(node_label)
        lbl.setFixedWidth(50)
        h.addWidget(lbl)

        ip_edit = QLineEdit()
        ip_edit.setPlaceholderText("IP address")
        ip_edit.setFixedWidth(120)

        port_spin = QSpinBox()
        port_spin.setRange(1024, 65535)
        port_spin.setValue(6789)
        port_spin.setFixedWidth(80)

        h.addWidget(ip_edit)
        h.addWidget(port_spin)

        # Mode buttons — SS, Berry, Singles, GTL
        modes = [
            ("SS",      "start:sweet_scent"),
            ("Berry",   "start:berry_farming"),
            ("Singles", "start:singles_farming"),
            ("GTL",     "start:gtl_sniper"),
        ]

        mode_btns = []
        for btn_label, cmd in modes:
            btn = QPushButton(btn_label)
            btn.setObjectName("btn_scan")
            btn.clicked.connect(
                lambda checked=False, nl=node_label, ip=ip_edit, p=port_spin, c=cmd:
                    self._send_node_command(nl, ip.text().strip(), p.value(), c)
            )
            h.addWidget(btn)
            mode_btns.append(btn)

        # Stop button
        btn_stop = QPushButton("Stop")
        btn_stop.setObjectName("btn_scan")
        btn_stop.clicked.connect(
            lambda checked=False, nl=node_label, ip=ip_edit, p=port_spin:
                self._send_node_command(nl, ip.text().strip(), p.value(), "stop")
        )
        h.addWidget(btn_stop)

        # Status label
        status_lbl = QLabel("—")
        status_lbl.setFixedWidth(50)
        status_lbl.setStyleSheet(
            "font-size: 11px; font-weight: bold; letter-spacing: 0.1em;"
        )
        h.addWidget(status_lbl)

        self._net_node_rows.append({
            "label":      node_label,
            "ip_edit":    ip_edit,
            "port_spin":  port_spin,
            "status_lbl": status_lbl,
        })

        return w

    def _send_node_command(self, node_label: str, host: str, port: int, command: str):
        """Send a command to a remote node in a daemon thread."""
        if not host:
            return

        def _worker():
            success = NetworkController.send_command(host, port, command)
            self.signals.network_command_result.emit(node_label, success)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_network_command_result(self, node_label: str, success: bool):
        """Update the status label for the node row (called on Qt thread via signal)."""
        for row in self._net_node_rows:
            if row["label"] == node_label:
                if success:
                    row["status_lbl"].setText("OK")
                    row["status_lbl"].setStyleSheet(
                        f"color: {C_ACCENT}; font-size: 11px; font-weight: bold; letter-spacing: 0.1em;"
                    )
                else:
                    row["status_lbl"].setText("FAILED")
                    row["status_lbl"].setStyleSheet(
                        f"color: {C_DANGER}; font-size: 11px; font-weight: bold; letter-spacing: 0.1em;"
                    )
                break
