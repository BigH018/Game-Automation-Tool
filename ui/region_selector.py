from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore  import Qt, pyqtSignal
from PyQt5.QtGui   import QColor, QPainter, QPen

from ui.stylesheet import C_ACCENT


class RegionSelector(QWidget):
    """
    Fullscreen overlay that lets the user click-and-drag to define a screen region.
    Emits region_selected(x, y, w, h) in screen coordinates, or cancelled() on ESC.
    """
    region_selected = pyqtSignal(int, int, int, int)
    cancelled       = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)

        screen = QApplication.primaryScreen()
        geom   = screen.geometry()
        self._screen_offset = geom.topLeft()

        # Grab a screenshot to use as the background so the overlay feels transparent
        self._bg = screen.grabWindow(0)

        self.setGeometry(geom)
        self._start = None
        self._end   = None
        self.setCursor(Qt.CrossCursor)

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawPixmap(0, 0, self._bg)
        # Dark vignette
        p.fillRect(self.rect(), QColor(0, 0, 0, 100))
        if self._start and self._end:
            x = min(self._start.x(), self._end.x())
            y = min(self._start.y(), self._end.y())
            w = abs(self._end.x() - self._start.x())
            h = abs(self._end.y() - self._start.y())
            # Highlight selected region
            p.fillRect(x, y, w, h, QColor(45, 232, 188, 55))
            pen = QPen(QColor(C_ACCENT), 2)
            p.setPen(pen)
            p.drawRect(x, y, w, h)
        p.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start = event.pos()
            self._end   = event.pos()

    def mouseMoveEvent(self, event):
        if self._start:
            self._end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._start:
            self._end = event.pos()
            x = min(self._start.x(), self._end.x())
            y = min(self._start.y(), self._end.y())
            w = abs(self._end.x() - self._start.x())
            h = abs(self._end.y() - self._start.y())
            self.close()
            if w > 5 and h > 5:
                ox = self._screen_offset.x()
                oy = self._screen_offset.y()
                self.region_selected.emit(x + ox, y + oy, w, h)
            else:
                self.cancelled.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            self.cancelled.emit()
