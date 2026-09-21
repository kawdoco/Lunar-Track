"""
wizard/setup_wizard.py
-------------------------
Wires the three step pages (When / Where / Review) into one guided flow.
"""

from PySide6 import QtCore, QtWidgets

from ..theme import Theme
from .step_indicator import StepIndicator
from .datetime_step_page import DateTimeStepPage
from .location_step_page import LocationStepPage
from .review_step_page import ReviewStepPage


class SetupWizard(QtWidgets.QWidget):
    """Three-step guided flow for entering observation settings.

    Used both for first-time setup (reached from Home) and for editing
    settings from the Moon view — the caller decides where "Cancel" or
    "Show Moon" should return to; this widget only knows about its own
    three steps.

    # OOP concept: COMPOSITION + POLYMORPHISM (via a common step interface)
    # -------------------------------------------------------------------
    # SetupWizard HOLDS one instance each of DateTimeStepPage,
    # LocationStepPage and ReviewStepPage (composition), placed inside a
    # QStackedWidget. In `_go_next()`, it calls `page.validate()` on
    # whichever page happens to be current WITHOUT checking which concrete
    # class it is - relying on the fact that both input steps share the
    # same `validate()` / `values()` contract from WizardStepPage. That is
    # polymorphism again, this time driving the wizard's navigation logic.
    #
    # # OOP concept: EVENT-DRIVEN COMMUNICATION (Signals / Observer pattern)
    # -------------------------------------------------------------------
    # `completed = QtCore.Signal(dict)` and `cancelled = QtCore.Signal()`
    # let SetupWizard announce "I'm done" without knowing who is
    # listening. MainWindow (in main_window.py) "observes" these signals
    # and reacts - a classic Observer-pattern relationship, kept loosely
    # coupled instead of SetupWizard calling MainWindow directly.
    """

    completed = QtCore.Signal(dict)
    cancelled = QtCore.Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._step = 0

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(60, 40, 60, 40)
        outer.setSpacing(22)

        top_bar = QtWidgets.QHBoxLayout()
        cancel_btn = QtWidgets.QPushButton("✕  Cancel")
        cancel_btn.setObjectName("ghost")
        cancel_btn.setCursor(QtCore.Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.cancelled.emit)
        title = QtWidgets.QLabel("Observation settings")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {Theme.TEXT};")
        top_bar.addWidget(cancel_btn)
        top_bar.addStretch(1)
        top_bar.addWidget(title)
        top_bar.addStretch(1)
        top_bar.addSpacing(cancel_btn.sizeHint().width())
        outer.addLayout(top_bar)

        self.indicator = StepIndicator()
        outer.addWidget(self.indicator)

        card = QtWidgets.QFrame()
        card.setObjectName("card")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(36, 30, 36, 30)

        self.stack = QtWidgets.QStackedWidget()
        self.step1 = DateTimeStepPage()
        self.step2 = LocationStepPage()
        self.step3 = ReviewStepPage()
        self.stack.addWidget(self.step1)
        self.stack.addWidget(self.step2)
        self.stack.addWidget(self.step3)
        card_layout.addWidget(self.stack)
        outer.addWidget(card, stretch=1)

        nav_row = QtWidgets.QHBoxLayout()
        self.back_btn = QtWidgets.QPushButton("←  Back")
        self.back_btn.setObjectName("secondary")
        self.back_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self._go_back)
        self.next_btn = QtWidgets.QPushButton("Next  →")
        self.next_btn.setObjectName("primary")
        self.next_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self._go_next)
        nav_row.addWidget(self.back_btn)
        nav_row.addStretch(1)
        nav_row.addWidget(self.next_btn)
        outer.addLayout(nav_row)

        self.step1.advance_requested.connect(self._go_next)
        self.step2.advance_requested.connect(self._go_next)
        self.step2.timezone_suggested.connect(self.step1.tz_combo.setCurrentText)

        self._sync_ui()

    def start(self, values: dict) -> None:
        """Opens the wizard at step 1, pre-filled with `values`."""
        self._step = 0
        self.step1.set_values(values)
        self.step1.show_error(None, None)
        self.step2.set_values(values)
        self.step2.show_error(None, None)
        self._sync_ui()

    def _go_next(self) -> None:
        page = self.stack.currentWidget()
        if hasattr(page, "validate"):
            bad_field, error = page.validate()
            page.show_error(bad_field, error)
            if error:
                return

        if self._step < 2:
            self._step += 1
            if self._step == 2:
                self.step3.set_summary(self._collect_values())
            self._sync_ui()
        else:
            self.completed.emit(self._collect_values())

    def _go_back(self) -> None:
        if self._step > 0:
            self._step -= 1
            self._sync_ui()

    def _collect_values(self) -> dict:
        values: dict = {}
        values.update(self.step1.values())
        values.update(self.step2.values())
        return values

    def _sync_ui(self) -> None:
        self.stack.setCurrentIndex(self._step)
        self.indicator.set_current(self._step)
        self.back_btn.setVisible(self._step > 0)
        self.next_btn.setText("Show Moon  🌙" if self._step == 2 else "Next  →")
