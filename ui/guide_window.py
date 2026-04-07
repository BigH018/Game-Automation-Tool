from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame,
)
from PyQt5.QtCore import Qt

from ui.stylesheet import DARK, LIGHT, _build_stylesheet
from ui.helpers    import _hline


class GuideWindow(QWidget):

    PAGES = [
        (
            "Welcome & Introduction",
            "Welcome to Shiny Hunt Tool — made by BigH!\n\n"
            "If you've ever done shiny hunting in Pokémon, you know the drill: "
            "press the same buttons hundreds of times, stare at the screen, "
            "and hope that 1 in 30000 odds finally land in your favour. It's tedious. "
            "This tool takes care of the button pressing for you.\n\n"
            "There are two things happening at once when the tool is running:\n"
            "  1. The macro presses keys automatically in a loop to trigger encounters.\n"
            "  2. The audio listener watches for the shiny encounter sound. "
            "When it hears it, the macro stops itself so you don't run from your shiny.\n\n"
            "Before you start, make sure you have:\n"
            "  • Your game running and in a position to use the macro\n"
            "  • Your game audio routed correctly to your PC\n\n"
            "Use the Back and Next buttons at the bottom to move between pages.\n\n"
            "Right, let's get you set up."
        ),
        (
            "The Settings Tab",
            "WAV File\n"
            "This is the audio template the tool listens for — the shiny encounter sound "
            "recorded from your game. The default is alert.wav in the tool's folder. "
            "If the file is missing or wrong, audio detection won't work. "
            "You can record your own using any audio recorder — just capture a few seconds "
            "of the shiny jingle and save it as a WAV file.\n\n\n"
            "Threshold\n"
            "This controls how closely the incoming audio has to match the template before "
            "the tool calls it a shiny. Too low (e.g. 0.1) and normal battle sounds might "
            "trigger a false positive. Too high (e.g. 0.9) and it might miss the real thing. "
            "Start at 0.3 and adjust only if you get false positives or missed detections.\n\n\n"
            "Scan Devices\n"
            "Click this before setting Device Index and Sample Rate. "
            "It will list every audio input device on your PC in the log below, "
            "with its index number and supported sample rates. "
            "Find your game capture or virtual audio device in that list.\n\n\n"
            "Device Index\n"
            "The number from the scan that matches your audio capture device. "
            "If this is wrong, the tool is listening to the wrong source and won't detect anything.\n\n\n"
            "Sample Rate\n"
            "How many audio samples per second the listener uses. 48000 works for most setups. "
            "Check the scan output — it shows which rates each device supports. "
            "Pick one that matches what your device actually supports.\n\n\n"
            "Hotkeys\n"
            "Sweet Scent starts/stops on F9, Berry Farming on F8, Singles Farming on F7 by default. "
            "Click Rebind next to any of them, then press your new key to change it. "
            "Press ESC during a rebind to cancel. "
            "Note: ESC quits the app entirely when you're NOT in rebind mode — so don't fat-finger it.\n\n\n"
            "Save / Load Settings\n"
            "Once everything is configured and working, hit Save Settings and pick a location. "
            "Next time you open the tool, hit Load Settings to restore everything in one click."
        ),
        (
            "Sweet Scent Farming",
            "Sweet Scent is a Pokémon move that instantly triggers a wild encounter "
            "without needing to walk through grass. It's perfect for farming because "
            "you can stand in one spot and spam it indefinitely.\n\n"
            "What the macro does, step by step:\n"
            "  1. Presses 'use/Abutton' use Sweet Scent\n"
            "  2. Waits for the battle to load (Battle Start Delay)\n"
            "  3. Presses the flee keys (S, D, E in random order) to run from the battle\n"
            "  4. Waits for the overworld to come back (Battle End Delay)\n"
            "  5. Repeats from step 1\n\n"
            "Status Dot Colours\n"
            "  • Teal = macro is running\n"
            "  • Red = idle / stopped\n"
            "  • Gold = shiny detected!\n\n"
            "Delay Settings\n"
            "Key Press Delay: how fast the flee keys are pressed one after another. "
            "Too fast and the game might miss an input. Too slow wastes time. "
            "The default range (28–160 ms) is fine for most situations.\n\n"
            "Battle Start Delay: how long the macro waits after using Sweet Scent "
            "before pressing the flee keys. If this is too short, it'll try to flee "
            "before the battle screen has even loaded. If too long, it's just sitting "
            "there doing nothing. Default is 12773–14500 ms — only change this if your "
            "game loads battles noticeably faster or slower.\n\n"
            "Battle End Delay: how long it waits after fleeing before starting the next cycle. "
            "Same idea — give the game time to return to the overworld. Default is 1800–4500 ms.\n\n"
            "Min/Max Variance\n"
            "Each delay is a random value between the min and max you set. "
            "This is intentional — a fixed delay pattern looks robotic. "
            "Random variance makes the timing more human-like. Don't set min equal to max.\n\n"
            "How to Start / Stop\n"
            "Press F9 (or your custom hotkey) to start. Press it again to stop. "
            "The status dot and label will update to reflect the current state.\n\n"
            "When a Shiny is Detected\n"
            "The macro stops automatically. The status turns gold. "
            "Check the event log — it will show the detection score so you can "
            "tell how confident the match was. Go catch your shiny!"
        ),
        (
            "Berry Farming — Coming Soon",
            "This mode isn't ready yet, but it's being worked on!\n\n"
            "Berry Farming will automate the process of farming berries in the overworld — "
            "walking to trees, interacting with them, and collecting what drops.\n\n"
            "Check back for updates. The tab is already there, just waiting to be filled in."
        ),
        (
            "Singles Farming — Coming Soon",
            "This one's still in the works too!\n\n"
            "Singles Farming will handle encounter-based farming where you fight "
            "rather than flee — useful for hunting shinies in situations where "
            "Sweet Scent isn't an option.\n\n"
            "Keep an eye out for updates."
        ),
        (
            "GTL Sniper",
            "GTL Sniping automatically refreshes the in-game trade listing and buys an item "
            "the moment its price drops to or below a target you set. "
            "All clicks use the same kernel-level Interception driver as the keyboard macros — "
            "no detectable Windows SendInput involved.\n\n\n"
            "Step 1 — Capture Coordinates\n"
            "The macro needs to know exactly where to click on your screen. "
            "You need to give it two positions:\n\n"
            "  • Refresh Button — wherever the GTL refresh/search button is on screen.\n"
            "  • Buy Button — wherever the buy confirmation button appears.\n\n"
            "To capture each one:\n"
            "  1. Click the Capture button next to the slot you want to set.\n"
            "  2. A 3-second countdown begins. Don't click anything yet.\n"
            "  3. Move your mouse over the target button in the game window.\n"
            "  4. Hold it there — coordinates are captured automatically when the timer hits zero.\n"
            "The label will update to show the captured (x, y) position. "
            "Repeat for the other slot. These are saved with your settings.\n\n\n"
            "Step 2 — Set the Price Region\n"
            "The macro reads the item price using OCR (optical character recognition). "
            "You need to tell it exactly where on screen the price number appears.\n\n"
            "  1. Click Set Region.\n"
            "  2. A fullscreen overlay appears over your screen.\n"
            "  3. Click and drag a rectangle tightly around the price number in the game.\n"
            "  4. Release the mouse — the region is saved automatically.\n"
            "  5. Press ESC at any time to cancel without saving.\n\n"
            "Tip: make the region as tight as possible around the digits only. "
            "Including extra UI chrome (borders, currency icons) can confuse the OCR.\n\n\n"
            "Step 3 — Set Max Buy Price\n"
            "This is the highest price (in pokeyen) you are willing to pay. "
            "If the OCR reads a price at or below this number, the macro clicks Buy and "
            "presses Spacebar to confirm the purchase.\n\n"
            "Setting Max Buy Price to 0 disables buying entirely — the macro will still "
            "refresh the listing but won't buy anything. Useful for testing that your "
            "coordinates and price region are set up correctly before going live.\n\n\n"
            "Refresh Rate\n"
            "How long the macro waits between each refresh click. "
            "This is randomised between the Min and Max values you set, same as the delay "
            "variance in Sweet Scent — random timing is less detectable than a fixed interval. "
            "The defaults (86–175 ms) are fast but human-looking. "
            "Don't set both values the same or the timing becomes a fixed pattern.\n\n\n"
            "How to Start / Stop\n"
            "Press F6 (or your custom hotkey) to start. Press it again to stop. "
            "The status dot turns teal when running and red when idle. "
            "GTL Sniper has no shiny detection — it only shows IDLE or RUNNING.\n\n\n"
            "Debug Mode\n"
            "By default the event log only prints when a purchase is made. "
            "Enable Debug Mode to also log every price the OCR reads each cycle. "
            "This is useful for checking your region is captured correctly and the "
            "OCR is reading the right number. Turn it off for normal sniping — "
            "the log floods quickly at 86–175 ms refresh rates.\n\n\n"
            "Requirements\n"
            "GTL Sniper needs Tesseract OCR installed to read prices. "
            "If you see OCR errors in the log, Tesseract is either missing or not "
            "at the expected path (C:\\Program Files\\Tesseract-OCR\\tesseract.exe). "
            "Download it from the UB-Mannheim GitHub page and install to the default location."
        ),
    ]

    def __init__(self, dark: bool, parent=None):
        super().__init__(parent, Qt.Window)
        self._dark = dark
        self._page = 0
        self.setWindowTitle("Guide — Shiny Hunt Tool")
        self.setMinimumSize(520, 440)
        self.resize(620, 540)
        self._build_ui()
        self._apply_style()
        self._update_page()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        self._lbl_title = QLabel()
        self._lbl_title.setObjectName("guide_title")
        self._lbl_title.setAlignment(Qt.AlignCenter)

        self._lbl_content = QLabel()
        self._lbl_content.setObjectName("guide_content")
        self._lbl_content.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._lbl_content.setWordWrap(True)

        scroll_container = QWidget()
        scroll_container.setObjectName("guide_scroll_container")
        scroll_layout = QVBoxLayout(scroll_container)
        scroll_layout.setContentsMargins(0, 4, 0, 4)
        scroll_layout.setSpacing(0)
        scroll_layout.addWidget(self._lbl_content)
        scroll_layout.addStretch()

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setWidget(scroll_container)

        self._btn_back = QPushButton("← Back")
        self._btn_next = QPushButton("Next →")
        btn_close = QPushButton("Close")

        self._btn_back.clicked.connect(self._go_back)
        self._btn_next.clicked.connect(self._go_next)
        btn_close.clicked.connect(self.close)

        nav = QHBoxLayout()
        nav.addWidget(self._btn_back)
        nav.addStretch()
        nav.addWidget(btn_close)
        nav.addStretch()
        nav.addWidget(self._btn_next)

        layout.addWidget(self._lbl_title)
        layout.addWidget(_hline())
        layout.addWidget(self._scroll, stretch=1)
        layout.addWidget(_hline())
        layout.addLayout(nav)

    def _update_page(self):
        title, content = self.PAGES[self._page]
        total = len(self.PAGES)
        self._lbl_title.setText(f"Page {self._page + 1} of {total} — {title}")
        self._lbl_content.setText(content)
        self._btn_back.setEnabled(self._page > 0)
        self._btn_next.setEnabled(self._page < total - 1)
        self._scroll.verticalScrollBar().setValue(0)

    def _go_back(self):
        if self._page > 0:
            self._page -= 1
            self._update_page()

    def _go_next(self):
        if self._page < len(self.PAGES) - 1:
            self._page += 1
            self._update_page()

    def _apply_style(self):
        c = DARK if self._dark else LIGHT
        self.setStyleSheet(_build_stylesheet(c))
