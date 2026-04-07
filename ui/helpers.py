from PyQt5.QtWidgets import QFrame, QLabel


def _hline():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Plain)
    return line


def _section(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setObjectName("section_title")
    return lbl
