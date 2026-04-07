from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QScrollArea, QFrame,
)
from PyQt5.QtCore import QTimer

from ui.helpers          import _hline, _section
from ui.region_selector  import RegionSelector


class GTLTabMixin:
    """Mixin providing GTL Sniper tab builder methods for MainWindow."""

    def _build_tab_gtl(self) -> QWidget:
        """GTL Sniper tab — coordinate capture, price region, settings."""
        macro = self.core.gtl_sniper

        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(14)

        v.addWidget(self._build_status_row("gtl"))
        v.addWidget(_hline())

        # ── Coordinates ──────────────────────────────────────────────────────
        v.addWidget(_section("Coordinates"))

        coords_widget = QWidget()
        cv = QVBoxLayout(coords_widget)
        cv.setContentsMargins(0, 4, 0, 4)
        cv.setSpacing(10)

        def _coord_display(coords):
            return f"({coords[0]}, {coords[1]})" if coords else "Not set"

        # Refresh Button row
        refresh_row = QWidget()
        rh = QHBoxLayout(refresh_row)
        rh.setContentsMargins(0, 0, 0, 0)
        rh.setSpacing(10)
        rh.addWidget(QLabel("Refresh Button"))
        self._lbl_gtl_refresh = QLabel(_coord_display(macro.refresh_coords))
        self._lbl_gtl_refresh.setObjectName("key_value")
        self._btn_gtl_capture_refresh = QPushButton("Capture")
        self._btn_gtl_capture_refresh.setObjectName("btn_rebind")
        self._btn_gtl_capture_refresh.setProperty("rebinding", "false")
        self._btn_gtl_capture_refresh.clicked.connect(
            lambda checked=False: self._start_coord_capture(
                "refresh_coords", self._lbl_gtl_refresh, self._btn_gtl_capture_refresh
            )
        )
        rh.addWidget(self._lbl_gtl_refresh)
        rh.addStretch()
        rh.addWidget(self._btn_gtl_capture_refresh)
        cv.addWidget(refresh_row)

        # Buy Button row
        buy_row = QWidget()
        bh = QHBoxLayout(buy_row)
        bh.setContentsMargins(0, 0, 0, 0)
        bh.setSpacing(10)
        bh.addWidget(QLabel("Buy Button"))
        self._lbl_gtl_buy = QLabel(_coord_display(macro.buy_coords))
        self._lbl_gtl_buy.setObjectName("key_value")
        self._btn_gtl_capture_buy = QPushButton("Capture")
        self._btn_gtl_capture_buy.setObjectName("btn_rebind")
        self._btn_gtl_capture_buy.setProperty("rebinding", "false")
        self._btn_gtl_capture_buy.clicked.connect(
            lambda checked=False: self._start_coord_capture(
                "buy_coords", self._lbl_gtl_buy, self._btn_gtl_capture_buy
            )
        )
        bh.addWidget(self._lbl_gtl_buy)
        bh.addStretch()
        bh.addWidget(self._btn_gtl_capture_buy)
        cv.addWidget(buy_row)

        v.addWidget(coords_widget)

        # ── Price Region ─────────────────────────────────────────────────────
        v.addWidget(_section("Price Region"))

        region_widget = QWidget()
        rv = QVBoxLayout(region_widget)
        rv.setContentsMargins(0, 4, 0, 4)
        rv.setSpacing(10)

        region_row = QWidget()
        rrh = QHBoxLayout(region_row)
        rrh.setContentsMargins(0, 0, 0, 0)
        rrh.setSpacing(10)
        rrh.addWidget(QLabel("Price Region"))

        def _region_display(r):
            return f"({r[0]}, {r[1]})  {r[2]}×{r[3]}" if r else "Not set"

        self._lbl_gtl_region = QLabel(_region_display(macro.price_region))
        self._lbl_gtl_region.setObjectName("key_value")
        self._btn_gtl_set_region = QPushButton("Set Region")
        self._btn_gtl_set_region.setObjectName("btn_rebind")
        self._btn_gtl_set_region.clicked.connect(self._open_region_selector)
        rrh.addWidget(self._lbl_gtl_region)
        rrh.addStretch()
        rrh.addWidget(self._btn_gtl_set_region)
        rv.addWidget(region_row)

        v.addWidget(region_widget)

        # ── Settings ─────────────────────────────────────────────────────────
        v.addWidget(_section("Settings"))

        settings_widget = QWidget()
        sv = QVBoxLayout(settings_widget)
        sv.setContentsMargins(0, 4, 0, 4)
        sv.setSpacing(10)

        # Max Buy Price
        price_row = QWidget()
        ph = QHBoxLayout(price_row)
        ph.setContentsMargins(0, 0, 0, 0)
        ph.setSpacing(8)
        ph.addWidget(QLabel("Max Buy Price"))
        ph.addStretch()
        spin_price = QSpinBox()
        spin_price.setRange(0, 999_999_999)
        spin_price.setSingleStep(1000)
        spin_price.setValue(macro.max_price)
        spin_price.setFixedWidth(110)
        spin_price.valueChanged.connect(lambda val: setattr(self.core.gtl_sniper, "max_price", val))
        self._spin_gtl_max_price = spin_price
        ph.addWidget(spin_price)
        ph.addWidget(QLabel("pokeyen"))
        sv.addWidget(price_row)

        # Refresh Rate (min / max — randomised each cycle)
        rate_row = QWidget()
        rath = QHBoxLayout(rate_row)
        rath.setContentsMargins(0, 0, 0, 0)
        rath.setSpacing(8)
        rath.addWidget(QLabel("Refresh rate"))
        rath.addStretch()

        spin_rate_min = QSpinBox()
        spin_rate_min.setRange(10, 30_000)
        spin_rate_min.setSingleStep(1)
        spin_rate_min.setValue(macro.refresh_rate_min)
        spin_rate_min.setFixedWidth(80)
        spin_rate_min.valueChanged.connect(
            lambda val: setattr(self.core.gtl_sniper, "refresh_rate_min", val)
        )
        self._spin_gtl_rate_min = spin_rate_min

        spin_rate_max = QSpinBox()
        spin_rate_max.setRange(10, 30_000)
        spin_rate_max.setSingleStep(1)
        spin_rate_max.setValue(macro.refresh_rate_max)
        spin_rate_max.setFixedWidth(80)
        spin_rate_max.valueChanged.connect(
            lambda val: setattr(self.core.gtl_sniper, "refresh_rate_max", val)
        )
        self._spin_gtl_rate_max = spin_rate_max

        rath.addWidget(spin_rate_min)
        rath.addWidget(QLabel("ms —"))
        rath.addWidget(spin_rate_max)
        rath.addWidget(QLabel("ms"))
        sv.addWidget(rate_row)

        v.addWidget(settings_widget)

        # ── Debug toggle ─────────────────────────────────────────────────────
        div2 = QFrame(); div2.setFrameShape(QFrame.HLine); div2.setFrameShadow(QFrame.Plain)
        v.addWidget(div2)
        v.addWidget(self._build_gtl_debug_toggle())

        v.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(w)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        return scroll

    def _build_gtl_debug_toggle(self) -> QWidget:
        """Debug Mode toggle row at the bottom of the GTL Sniper tab."""
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 2, 0, 2)
        h.setSpacing(10)

        self._btn_gtl_debug_toggle = QPushButton("Debug Mode")
        self._btn_gtl_debug_toggle.setObjectName("btn_debug_toggle")
        self._btn_gtl_debug_toggle.setProperty("debug_on", "false")
        self._btn_gtl_debug_toggle.clicked.connect(self._toggle_gtl_debug_mode)

        h.addWidget(self._btn_gtl_debug_toggle)
        h.addStretch()
        return w

    def _toggle_gtl_debug_mode(self):
        """Flip debug mode on the GTL Sniper macro and update the button appearance."""
        macro = self.core.gtl_sniper
        macro.debug = not macro.debug
        self._btn_gtl_debug_toggle.setProperty("debug_on", "true" if macro.debug else "false")
        self._btn_gtl_debug_toggle.setStyle(self._btn_gtl_debug_toggle.style())

    # ── GTL coordinate capture ────────────────────────────────

    def _start_coord_capture(self, attr: str, lbl, btn, target=None):
        """Begin a 3-second countdown then capture the cursor position.

        `target` is the object on which the captured (x, y) tuple will be
        stored at attribute `attr`. Defaults to `self.core.gtl_sniper` for
        backward compatibility with the existing GTL Sniper capture buttons.
        """
        if self._coord_timer is not None:
            return  # capture already in progress
        self._coord_capture_target = target if target is not None else self.core.gtl_sniper
        self._coord_capture_attr   = attr
        self._coord_capture_lbl    = lbl
        self._coord_capture_btn    = btn
        self._coord_capture_count  = 3

        btn.setEnabled(False)
        btn.setText("3…")
        btn.setProperty("rebinding", "true")
        btn.setStyle(btn.style())

        self._append_log("Hover over the target button — capturing in 3 s…")
        self._coord_timer = QTimer(self)
        self._coord_timer.timeout.connect(self._coord_capture_tick)
        self._coord_timer.start(1000)

    def _coord_capture_tick(self):
        self._coord_capture_count -= 1
        if self._coord_capture_count > 0:
            self._coord_capture_btn.setText(f"{self._coord_capture_count}…")
            return

        self._coord_timer.stop()
        self._coord_timer = None

        from PyQt5.QtGui import QCursor
        pos = QCursor.pos()
        x, y = pos.x(), pos.y()
        target = self._coord_capture_target or self.core.gtl_sniper
        setattr(target, self._coord_capture_attr, (x, y))

        self._coord_capture_lbl.setText(f"({x}, {y})")
        self._coord_capture_btn.setText("Capture")
        self._coord_capture_btn.setEnabled(True)
        self._coord_capture_btn.setProperty("rebinding", "false")
        self._coord_capture_btn.setStyle(self._coord_capture_btn.style())
        self._append_log(f"Captured {self._coord_capture_attr}: ({x}, {y})")

        self._coord_capture_target = None
        self._coord_capture_attr = None
        self._coord_capture_lbl  = None
        self._coord_capture_btn  = None

    # ── GTL region selector ───────────────────────────────────

    def _open_region_selector(self):
        """Show the fullscreen drag-to-select overlay."""
        self._region_selector = RegionSelector()
        self._region_selector.region_selected.connect(self._on_region_selected)
        self._region_selector.cancelled.connect(lambda: self._append_log("Price region selection cancelled."))
        self._region_selector.show()
        self._region_selector.activateWindow()
        self._region_selector.raise_()

    def _on_region_selected(self, x: int, y: int, w: int, h: int):
        self.core.gtl_sniper.price_region = (x, y, w, h)
        self._lbl_gtl_region.setText(f"({x}, {y})  {w}×{h}")
        self._append_log(f"Price region set: ({x}, {y})  {w}×{h} px")
