"""
notifications.py — Discord + ntfy.sh notifications for shiny detection.

Discord webhook URL is configurable via the UI and persisted in settings.
The ntfy.sh topic is fixed (Shiny-Detected) and fires alongside Discord
whenever notifications are enabled.
"""

import threading
from datetime import datetime


def _get_requests():
    """Lazy import — retries every call so a transient startup failure doesn't stick."""
    try:
        import requests
        return requests
    except Exception:
        return None


class NotificationManager:
    """
    Sends shiny detection alerts through two channels in parallel:
      - Discord webhook (URL + enabled toggle, configured via UI, persisted)
      - ntfy.sh topic (fixed — 'Shiny-Detected', always fires when enabled)

    Both channels are gated by the single `enabled` flag. Discord additionally
    requires `webhook_url` to be set; if it is empty, only ntfy.sh fires.
    """

    NTFY_URL = "https://ntfy.sh/Shiny-Detected"

    def __init__(self):
        self.webhook_url = ""
        self.enabled     = False

        # Callback — set by the coordinator
        self.on_log = None   # (message: str)

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)
        else:
            print(msg)

    # ── Discord ────────────────────────────────────────────────

    def _post_discord(self, payload: dict):
        """Send a POST request to the Discord webhook URL. Runs in a background thread."""
        requests = _get_requests()
        if requests is None:
            self._log("Discord notification skipped — requests library missing.")
            return
        if not self.webhook_url:
            return
        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            if resp.status_code in (200, 204):
                self._log("Discord notification delivered successfully.")
            else:
                self._log(f"Discord webhook returned status {resp.status_code}.")
        except Exception as exc:
            self._log(f"Discord notification failed: {exc}")

    # ── ntfy.sh ────────────────────────────────────────────────

    def _post_ntfy(self, message: str, title: str, tags: str = "sparkles", priority: str = "high"):
        """Send a POST request to the ntfy.sh topic. Runs in a background thread."""
        requests = _get_requests()
        if requests is None:
            self._log("ntfy.sh notification skipped — requests library missing.")
            return
        try:
            resp = requests.post(
                self.NTFY_URL,
                data=message.encode("utf-8"),
                headers={
                    "Title":    title,
                    "Tags":     tags,
                    "Priority": priority,
                },
                timeout=10,
            )
            if resp.status_code in (200, 204):
                self._log("ntfy.sh notification delivered successfully.")
            else:
                self._log(f"ntfy.sh returned status {resp.status_code}.")
        except Exception as exc:
            self._log(f"ntfy.sh notification failed: {exc}")

    # ── Public API ─────────────────────────────────────────────

    def send_shiny_alert(self, score: float):
        """Send a shiny detection alert through both channels. Runs in background threads."""
        if not self.enabled:
            return
        now = datetime.now().strftime("%H:%M:%S")

        # Discord — only if a webhook URL is configured
        if self.webhook_url:
            discord_payload = {
                "content": (
                    f"@here ✨ **Shiny detected!**\n"
                    f"Detection score: {score:.4f}\n"
                    f"Time: {now}\n"
                    f"Good luck catching it!"
                ),
                "allowed_mentions": {"parse": ["everyone"]},
            }
            threading.Thread(target=self._post_discord, args=(discord_payload,), daemon=True).start()

        # ntfy.sh — topic is fixed, always fires when notifications are enabled
        ntfy_message = (
            f"Detection score: {score:.4f}\n"
            f"Time: {now}\n"
            f"Good luck catching it!"
        )
        threading.Thread(
            target=self._post_ntfy,
            args=(ntfy_message, "Shiny detected!"),
            daemon=True,
        ).start()

    def send_test_message(self):
        """Send a test notification through both channels. Runs in background threads."""
        # Discord — only if a webhook URL is set
        if self.webhook_url:
            discord_payload = {
                "content": (
                    "@here 🔔 **Test notification from Shiny Hunt Tool — BigH**\n"
                    "If you can see this your webhook is set up correctly!"
                ),
                "allowed_mentions": {"parse": ["everyone"]},
            }
            threading.Thread(target=self._post_discord, args=(discord_payload,), daemon=True).start()

        # ntfy.sh test — always fires
        threading.Thread(
            target=self._post_ntfy,
            args=(
                "Test notification from Shiny Hunt Tool — BigH. "
                "If you can see this, your ntfy.sh topic is set up correctly!",
                "Test notification",
                "bell",
                "default",
            ),
            daemon=True,
        ).start()

    def check_available(self) -> bool:
        """Log a warning at startup if requests is missing. Returns True if available."""
        if _get_requests() is None:
            self._log("Notifications unavailable — requests library missing.")
            return False
        return True
