"""
main.py
--------
The application's entry point. Deliberately tiny: everything interesting
lives in the classes it wires together.
"""

import sys

from PySide6 import QtWidgets

from .theme import STYLE_SHEET
from .main_window import MainWindow


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    # Force the cross-platform "Fusion" style before applying our own QSS.
    # Without this, Windows keeps rendering some widgets (editable combo
    # boxes especially - e.g. the timezone field) with its native
    # "windowsvista" style underneath our stylesheet. That native style
    # does its own custom painting for parts of the widget our QSS
    # doesn't fully cover, which is what caused the timezone combo box to
    # show garbled, overlapping text on Windows - the native paint and
    # our stylesheet paint were both drawing into the same region.
    # Fusion is a QSS-friendly style that doesn't fight with stylesheets
    # like this, so switching to it fixes the rendering everywhere, not
    # just for this one field.
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE_SHEET)
    window = MainWindow()   # composition root - see main_window.py
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
