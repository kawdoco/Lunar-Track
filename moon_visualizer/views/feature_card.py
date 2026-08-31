"""
views/feature_card.py
-----------------------
A tiny reusable info card used three times on the Home page.
"""

from PySide6 import QtWidgets

from ..theme import Theme


class FeatureCard(QtWidgets.QFrame):
    """A small info card used on the Home page.

    # OOP concept: REUSABILITY THROUGH A CLASS + CONSTRUCTOR PARAMETERS
    # -------------------------------------------------------------------
    # Instead of duplicating the same block of layout code three times on
    # HomePage, that layout is captured once inside a class whose
    # `__init__` takes (emoji, title, body) as parameters. Every card is
    # then just `FeatureCard("🌗", "...", "...")` - a fresh OBJECT built
    # from the same class blueprint but configured with different data.
    """

    def __init__(self, emoji: str, title: str, body: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        top = QtWidgets.QLabel(f"{emoji}  {title}")
        top.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Theme.TEXT};")
        body_lbl = QtWidgets.QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(f"color: {Theme.TEXT_DIM};")

        layout.addWidget(top)
        layout.addWidget(body_lbl)
