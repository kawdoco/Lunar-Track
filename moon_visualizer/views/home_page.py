"""
views/home_page.py
--------------------
The landing page: intro + two ways into the app.
"""

from PySide6 import QtCore, QtWidgets

from .feature_card import FeatureCard


class HomePage(QtWidgets.QWidget):
    """Landing page: intro + two ways in — a guided setup, or a one-click
    shortcut straight to the visualizer with default settings.

    # OOP concept: COMPOSITION + SIGNALS (Observer pattern)
    # -------------------------------------------------------------------
    # HomePage is built out of three FeatureCard objects (composition) and
    # exposes two Signals (`setup_requested`, `quick_launch_requested`)
    # instead of importing MainWindow and calling it directly. This keeps
    # HomePage fully independent of whoever uses it - MainWindow is the
    # one that "observes" these signals and decides what happens next.
    """

    setup_requested = QtCore.Signal()
    quick_launch_requested = QtCore.Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(60, 50, 60, 50)
        outer.setSpacing(24)
        outer.addStretch(1)

        title = QtWidgets.QLabel("🌙  Moon Visualizer")
        title.setObjectName("h1")
        title.setAlignment(QtCore.Qt.AlignCenter)

        subtitle = QtWidgets.QLabel(
            "See exactly how the Moon looks — its phase, illumination and\n"
            "position in the sky — for any date, time and place on Earth."
        )
        subtitle.setObjectName("h2")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)

        outer.addWidget(title)
        outer.addWidget(subtitle)

        cards_row = QtWidgets.QHBoxLayout()
        cards_row.setSpacing(16)
        cards_row.addWidget(FeatureCard(
            "🌗", "Realistic phase disk",
            "A true-to-life waxing/waning Moon rendered from the actual "
            "phase angle for your chosen moment."))
        cards_row.addWidget(FeatureCard(
            "🧭", "Sky position",
            "A compass-style sky dome shows altitude & azimuth — whether "
            "the Moon is up at all, right now."))
        cards_row.addWidget(FeatureCard(
            "⏱️", "Time-lapse mode",
            "Hit play and watch the Moon phase evolve automatically, at a "
            "speed and step size you control."))
        outer.addLayout(cards_row)

        launch_btn = QtWidgets.QPushButton("Set up observation  →")
        launch_btn.setObjectName("primary")
        launch_btn.setCursor(QtCore.Qt.PointingHandCursor)
        launch_btn.clicked.connect(self.setup_requested.emit)
        launch_row = QtWidgets.QHBoxLayout()
        launch_row.addStretch(1)
        launch_row.addWidget(launch_btn)
        launch_row.addStretch(1)
        outer.addLayout(launch_row)

        quick_btn = QtWidgets.QPushButton("Or jump in with default settings")
        quick_btn.setObjectName("ghost")
        quick_btn.setCursor(QtCore.Qt.PointingHandCursor)
        quick_btn.clicked.connect(self.quick_launch_requested.emit)
        quick_row = QtWidgets.QHBoxLayout()
        quick_row.addStretch(1)
        quick_row.addWidget(quick_btn)
        quick_row.addStretch(1)
        outer.addLayout(quick_row)

        outer.addStretch(2)
