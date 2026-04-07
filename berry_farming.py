"""
berry_farming.py — BerryFarmingMacro: key-press automation for the Berry Farming method.
"""

import time, random, threading

try:
    import interception
except ImportError:
    raise ImportError("interception-python is not installed. Run: pip install interception-python")


class BerryFarmingMacro:
    """
    Automates the Berry Farming snake-pattern loop.
    Communicates with the coordinator via on_start, on_stop, and on_log callbacks.
    """

    def __init__(self):
        self.running       = False
        self._stop_event   = threading.Event()
        self._macro_thread = None

        # Configurable key bindings
        self.use_key        = "e"   # interact / confirm / plant
        self.water_key      = "4"   # water action (bindable)
        self.move_right_key = "d"   # move right
        self.move_left_key  = "a"   # move left
        self.look_down_key  = "s"   # face down toward spot
        self.look_up_key    = "w"   # face up toward spot
        self.repel_key      = "5"   # use repel (bindable)
        self.map_key        = "1"   # open map (bindable) — Complete Farm

        # Complete Farm — fly destination (set from UI, same capture flow as GTL)
        self.fly_coords = (1255, 549)   # (x, y) screen coords of the farm on the map

        # Mode toggles — set by the UI, never persisted
        self.debug = False
        self.mode = "plant"   # "plant" | "water" | "pickup"
        self.size = "full"    # "full" | "single" | "full2" | "complete"

        # Configurable delays (milliseconds)
        self.action_delay_min        = 220
        self.action_delay_max        = 300
        self.move_delay_min          = 200
        self.move_delay_max          = 280
        self.post_interact_delay_min = 250
        self.post_interact_delay_max = 320
        self.step_hold_duration_min  = 100
        self.step_hold_duration_max  = 145

        # Pickup-specific delays (milliseconds)
        self.pickup_delay_min        = 940
        self.pickup_delay_max        = 1100

        # Surf delays (milliseconds) — Shrine only
        self.surf_delay_min          = 1000
        self.surf_delay_max          = 2000
        self.surf_start_delay_min    = 3000
        self.surf_start_delay_max    = 4000
        self.surf_move_delay_min     = 100
        self.surf_move_delay_max     = 150
        self.surf_end_delay_min      = 3000
        self.surf_end_delay_max      = 4000

        # Fly delays (milliseconds) — Complete Farm only
        self.fly_delay_min           = 7000
        self.fly_delay_max           = 7500

        # Callbacks — set by the coordinator
        self.on_start = None   # ()
        self.on_stop  = None   # ()
        self.on_log   = None   # (message: str)

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)

    def _tap(self, key: str):
        interception.press(key)

    def _hold(self, key: str):
        ms = random.randint(self.step_hold_duration_min, self.step_hold_duration_max)
        interception.key_down(key)
        time.sleep(ms / 1000)
        interception.key_up(key)
        if self.debug:
            self._log(f"[DEBUG] Held {key} for {ms}ms")

    def _wait_action(self) -> int:
        ms = random.randint(self.action_delay_min, self.action_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _wait_move(self) -> int:
        ms = random.randint(self.move_delay_min, self.move_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _wait_pickup(self) -> int:
        ms = random.randint(self.pickup_delay_min, self.pickup_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _wait_post_interact(self) -> int:
        ms = random.randint(self.post_interact_delay_min, self.post_interact_delay_max)
        time.sleep(ms / 1000)
        return ms

    # ── Helpers ───────────────────────────────────────────────

    def _steps(self, key: str, count: int):
        """Hold a direction key `count` times to walk that many steps."""
        for _ in range(count):
            if not self.running:
                return
            self._hold(key)
            self._wait_move()

    def _wait_surf_move(self) -> int:
        ms = random.randint(self.surf_move_delay_min, self.surf_move_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _surf_steps(self, key: str, count: int):
        """Tap a direction key `count` times while surfing (faster movement)."""
        for _ in range(count):
            if not self.running:
                return
            self._tap(key)
            self._wait_surf_move()

    def _wait_surf(self) -> int:
        ms = random.randint(self.surf_delay_min, self.surf_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _wait_surf_start(self) -> int:
        ms = random.randint(self.surf_start_delay_min, self.surf_start_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _wait_surf_end(self) -> int:
        ms = random.randint(self.surf_end_delay_min, self.surf_end_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _single_patch(self):
        """One single patch: row 1 right (6 spots), transition, row 2 left (6 spots)."""

        # Row 1 — right, facing down
        for i in range(6):
            if not self.running:
                return
            self._plant_and_water()
            if i < 5:
                self._move_right()

        # Transition to row 2
        if not self.running:
            return
        self._hold(self.move_right_key)
        self._wait_move()

        for _ in range(3):
            self._hold(self.look_down_key)
            self._wait_move()

        self._hold(self.move_left_key)
        self._wait_move()

        self._tap(self.look_up_key)
        self._wait_move()

        # Row 2 — left, facing up
        for i in range(6):
            if not self.running:
                return
            self._plant_and_water()
            if i < 5:
                self._move_left()

    def _plant_and_water(self):
        if self.mode == "water":
            self._tap(self.water_key)
            ms = self._wait_action()
            if self.debug:
                self._log(f"[DEBUG] Pressed water ({self.water_key}) — action {ms}ms")
            return

        if self.mode == "pickup":
            self._tap(self.use_key)
            ms = self._wait_pickup()
            if self.debug:
                self._log(f"[DEBUG] Pressed use ({self.use_key}) — pickup {ms}ms")
            self._tap(self.use_key)
            ms = self._wait_action()
            if self.debug:
                self._log(f"[DEBUG] Pressed use ({self.use_key}) — action {ms}ms")
            return

        self._tap(self.use_key)
        ms = self._wait_post_interact()
        if self.debug:
            self._log(f"[DEBUG] Pressed use ({self.use_key}) — post-interact {ms}ms")

        self._tap(self.use_key)
        ms = self._wait_action()
        if self.debug:
            self._log(f"[DEBUG] Pressed use ({self.use_key}) — action {ms}ms")

        self._tap(self.water_key)
        ms = self._wait_action()
        if self.debug:
            self._log(f"[DEBUG] Pressed water ({self.water_key}) — action {ms}ms")

    def _move_right(self):
        self._hold(self.move_right_key)
        ms = self._wait_move()
        if self.debug:
            self._log(f"[DEBUG] Stepped right ({self.move_right_key}) — move {ms}ms")

        self._tap(self.look_down_key)
        ms = self._wait_move()
        if self.debug:
            self._log(f"[DEBUG] Faced down ({self.look_down_key}) — move {ms}ms")

    def _move_left(self):
        self._hold(self.move_left_key)
        ms = self._wait_move()
        if self.debug:
            self._log(f"[DEBUG] Stepped left ({self.move_left_key}) — move {ms}ms")

        self._tap(self.look_up_key)
        ms = self._wait_move()
        if self.debug:
            self._log(f"[DEBUG] Faced up ({self.look_up_key}) — move {ms}ms")

    # ── Snake block ───────────────────────────────────────────

    def _snake_block(self, first_block=False):
        """One full snake pass (rows 1 + 2)."""

        # Row 1 — right, looking down
        first_count = 5 if (first_block and self.mode == "plant") else 6
        for i in range(first_count):
            if not self.running:
                return
            self._plant_and_water()
            if i < first_count - 1:
                self._move_right()

        # Gap cross: 4× move_right (hold), then face down (tap)
        if not self.running:
            return
        for _ in range(4):
            self._hold(self.move_right_key)
            self._wait_move()
        self._tap(self.look_down_key)
        self._wait_move()

        for i in range(6):
            if not self.running:
                return
            self._plant_and_water()
            if i < 5:
                self._move_right()

        # Transition to row 2
        if not self.running:
            return
        self._hold(self.move_right_key)
        self._wait_move()

        for _ in range(3):
            self._hold(self.look_down_key)
            self._wait_move()

        self._hold(self.move_left_key)
        self._wait_move()

        self._tap(self.look_up_key)
        self._wait_move()

        # Row 2 — left, looking up
        for i in range(6):
            if not self.running:
                return
            self._plant_and_water()
            if i < 5:
                self._move_left()

        # Gap cross: 4× move_left (hold), then face up (tap)
        if not self.running:
            return
        for _ in range(4):
            self._hold(self.move_left_key)
            self._wait_move()
        self._tap(self.look_up_key)
        self._wait_move()

        for i in range(6):
            if not self.running:
                return
            self._plant_and_water()
            if i < 5:
                self._move_left()

    # ── Single patch ─────────────────────────────────────────

    def _run_single_macro(self):
        interception.auto_capture_devices()
        time.sleep(0.1)

        self._single_patch()

        self._finish()

    # ── Main loop ─────────────────────────────────────────────

    def _run_macro(self):
        interception.auto_capture_devices()
        time.sleep(0.1)
        self._do_full_farm()
        self._finish()

    def _do_full_farm(self):
        """Mistralton body (3 snake blocks). No device capture, no _finish()."""
        # Block 1
        self._snake_block(first_block=True)
        if not self.running:
            return

        # Move down 2 rows
        self._hold(self.look_down_key)
        self._wait_move()
        self._hold(self.look_down_key)
        self._wait_move()

        # Block 2
        self._snake_block()
        if not self.running:
            return

        # Move down 2 rows
        self._hold(self.look_down_key)
        self._wait_move()
        self._hold(self.look_down_key)
        self._wait_move()

        # Block 3
        self._snake_block()

    # ── Shrine ───────────────────────────────────────────────

    def _run_full2_macro(self):
        interception.auto_capture_devices()
        time.sleep(0.1)
        self._do_full_farm2()
        self._finish()

    def _do_full_farm2(self):
        """Shrine body (7 patches + surf). No device capture, no _finish()."""
        # Navigate to patch 1
        self._steps(self.move_right_key, 6)
        if not self.running: return
        self._steps(self.look_up_key, 4)
        if not self.running: return
        self._steps(self.move_right_key, 3)
        if not self.running: return
        self._tap(self.look_down_key)
        self._wait_move()

        # Patch 1
        self._single_patch()
        if not self.running: return

        # Navigate to patch 2
        self._steps(self.move_left_key, 3)
        if not self.running: return
        self._steps(self.look_up_key, 6)
        if not self.running: return
        self._steps(self.move_right_key, 1)
        if not self.running: return
        self._steps(self.look_up_key, 2)
        if not self.running: return
        self._steps(self.move_right_key, 1)
        if not self.running: return
        self._steps(self.look_up_key, 3)
        if not self.running: return
        self._steps(self.move_right_key, 1)
        if not self.running: return
        self._tap(self.look_down_key)
        self._wait_move()

        # Patch 2
        self._single_patch()
        if not self.running: return

        # Use repel
        self._steps(self.move_left_key, 2)
        if not self.running: return
        self._tap(self.repel_key)
        ms = self._wait_action()
        if self.debug:
            self._log(f"[DEBUG] Pressed repel ({self.repel_key}) — action {ms}ms")

        # Navigate to patch 3
        self._steps(self.move_left_key, 11)
        if not self.running: return
        self._steps(self.look_up_key, 3)
        if not self.running: return
        self._steps(self.move_right_key, 1)
        if not self.running: return
        self._tap(self.look_down_key)
        self._wait_move()

        # Patch 3
        self._single_patch()
        if not self.running: return

        # Navigate to patch 4
        self._steps(self.move_left_key, 1)
        if not self.running: return
        self._steps(self.look_down_key, 2)
        if not self.running: return
        self._steps(self.move_left_key, 16)
        if not self.running: return
        self._steps(self.look_down_key, 1)
        if not self.running: return

        # Patch 4
        self._single_patch()
        if not self.running: return

        # Navigate to patch 5
        self._steps(self.move_left_key, 2)
        if not self.running: return
        self._steps(self.look_up_key, 12)
        if not self.running: return
        self._steps(self.move_right_key, 1)
        if not self.running: return
        self._tap(self.look_down_key)
        self._wait_move()

        # Patch 5
        self._single_patch()
        if not self.running: return

        # Navigate to patch 6
        self._steps(self.move_left_key, 1)
        if not self.running: return
        self._steps(self.look_up_key, 7)
        if not self.running: return
        self._steps(self.move_left_key, 4)
        if not self.running: return
        self._steps(self.look_up_key, 3)
        if not self.running: return
        self._steps(self.move_right_key, 1)
        if not self.running: return
        self._tap(self.look_down_key)
        self._wait_move()

        # Patch 6
        self._single_patch()
        if not self.running: return

        # Navigate to patch 7 (surf crossing)
        self._steps(self.move_right_key, 9)
        if not self.running: return
        self._steps(self.look_up_key, 9)
        if not self.running: return
        self._steps(self.move_right_key, 3)
        if not self.running: return
        self._steps(self.look_up_key, 5)
        if not self.running: return
        self._steps(self.move_right_key, 5)
        if not self.running: return

        # Start surfing
        self._tap(self.use_key)
        ms = self._wait_surf()
        if self.debug:
            self._log(f"[DEBUG] Pressed use ({self.use_key}) — surf interact {ms}ms")
        self._tap(self.use_key)
        ms = self._wait_surf()
        if self.debug:
            self._log(f"[DEBUG] Pressed use ({self.use_key}) — surf confirm {ms}ms")

        ms = self._wait_surf_start()
        if self.debug:
            self._log(f"[DEBUG] Waited surf start — {ms}ms")

        # Surf across
        self._surf_steps(self.move_right_key, 8)
        if not self.running: return

        # Wait to get off surfing
        ms = self._wait_surf_end()
        if self.debug:
            self._log(f"[DEBUG] Waited surf end — {ms}ms")

        # Navigate to patch 7
        self._steps(self.move_right_key, 3)
        if not self.running: return
        self._steps(self.look_down_key, 3)
        if not self.running: return
        self._steps(self.move_right_key, 1)
        if not self.running: return
        self._tap(self.look_down_key)
        self._wait_move()

        # Patch 7
        self._single_patch()

    # ── Complete Farm (Mistralton → fly → Shrine) ────────────

    def _click(self, coords: tuple):
        """Move to (x, y) and left-click via the Interception driver."""
        x, y = coords
        interception.move_to(x, y)
        time.sleep(0.05)
        interception.left_click()

    def _wait_fly(self) -> int:
        ms = random.randint(self.fly_delay_min, self.fly_delay_max)
        time.sleep(ms / 1000)
        return ms

    def _run_complete_macro(self):
        interception.auto_capture_devices()
        time.sleep(0.1)

        # 1. Mistralton
        self._do_full_farm()
        if not self.running:
            self._finish()
            return

        # 2. Press map key to open the town map
        self._tap(self.map_key)
        ms = self._wait_action()
        if self.debug:
            self._log(f"[DEBUG] Pressed map ({self.map_key}) — action {ms}ms")

        # 3. Click fly destination twice (select + confirm)
        if self.fly_coords is None:
            self._log("Fly location not set — aborting Complete Farm.")
            self._finish()
            return

        self._click(self.fly_coords)
        ms = self._wait_action()
        if self.debug:
            self._log(f"[DEBUG] Clicked fly location {self.fly_coords} — action {ms}ms")
        self._click(self.fly_coords)
        if self.debug:
            self._log(f"[DEBUG] Confirmed fly location {self.fly_coords}")

        # 4. Fly delay — wait for map transition / landing animation
        ms = self._wait_fly()
        if self.debug:
            self._log(f"[DEBUG] Waited fly delay — {ms}ms")

        if not self.running:
            self._finish()
            return

        # 5. Shrine
        self._do_full_farm2()

        self._finish()

    def _finish(self):
        self.running = False
        self._log("Macro stopped.")
        if self.on_stop:
            self.on_stop()

    def start(self):
        if self.running:
            return
        self._stop_event.clear()
        self.running = True
        targets = {
            "single":   self._run_single_macro,
            "full":     self._run_macro,
            "full2":    self._run_full2_macro,
            "complete": self._run_complete_macro,
        }
        target = targets.get(self.size, self._run_macro)
        self._macro_thread = threading.Thread(target=target, daemon=True)
        self._macro_thread.start()
        labels = {
            "single":   "single patch",
            "full":     "Mistralton",
            "full2":    "Shrine",
            "complete": "complete farm",
        }
        label = labels.get(self.size, self.size)
        self._log(f"Macro started. ({label})")
        if self.on_start:
            self.on_start()

    def stop(self):
        self.running = False
        self._stop_event.set()
