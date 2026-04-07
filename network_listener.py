import socket
import threading


class NetworkListener:
    """
    TCP socket server that listens for remote start/stop commands.
    Runs on the farm machine; each connection is handled in its own daemon thread.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 6789):
        self.host    = host
        self.port    = port
        self.running = False

        self.on_log     = None   # callback(msg: str)
        self.on_command = None   # callback(command: str)

        self._server_socket = None
        self._accept_thread = None

    # ── Internal helpers ─────────────────────────────────────

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def _handle_client(self, conn: socket.socket, addr):
        """Handle a single client connection in its own thread."""
        try:
            data = conn.recv(1024).decode("utf-8").strip()
            if not data:
                return

            self._log(f"Network: received '{data}' from {addr[0]}:{addr[1]}")

            if data == "ping":
                conn.sendall(b"pong")
                return

            valid_commands = (
                "start:sweet_scent",
                "start:berry_farming",
                "start:singles_farming",
                "start:gtl_sniper",
                "stop",
            )

            if data in valid_commands:
                conn.sendall(b"ok")
                if self.on_command:
                    self.on_command(data)
            else:
                conn.sendall(b"unknown")
                self._log(f"Network: unknown command '{data}'")
        except Exception as exc:
            self._log(f"Network: client error — {exc}")
        finally:
            conn.close()

    def _accept_loop(self):
        """Accept incoming connections until the server socket is closed."""
        while self.running:
            try:
                conn, addr = self._server_socket.accept()
                t = threading.Thread(
                    target=self._handle_client, args=(conn, addr), daemon=True
                )
                t.start()
            except OSError:
                # Socket was closed by stop_listening()
                break

    # ── Public API ───────────────────────────────────────────

    def start_listening(self):
        """Bind socket and start the accept loop in a daemon thread."""
        if self.running:
            return

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(4)
        self.running = True

        self._accept_thread = threading.Thread(
            target=self._accept_loop, daemon=True
        )
        self._accept_thread.start()

        self._log(f"Network listener started on port {self.port}")
        self._log(
            f"If connections are refused run as admin: "
            f"netsh advfirewall firewall add rule name=BH-Tools-Listener "
            f"dir=in action=allow protocol=TCP localport={self.port}"
        )

    def stop_listening(self):
        """Close the server socket and stop accepting connections."""
        if not self.running:
            return
        self.running = False
        try:
            self._server_socket.close()
        except Exception:
            pass
        self._log("Network listener stopped")
