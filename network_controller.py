import socket


class NetworkController:
    """
    Sends commands from the main machine to a farm machine over TCP.
    Stateless — all methods are static.
    """

    @staticmethod
    def send_command(host: str, port: int, command: str) -> bool:
        """
        Open a TCP connection, send the command string, wait for 'ok', close.
        Returns True on success, False on any error (timeout, refused, etc.).
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((host, port))
            sock.sendall(command.encode("utf-8"))
            response = sock.recv(1024).decode("utf-8").strip()
            sock.close()
            return response == "ok"
        except Exception:
            return False
