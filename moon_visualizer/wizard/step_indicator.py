"""
wizard/step_indicator.py
--------------------------
The horizontal "1 - 2 - 3" progress stepper shown above the wizard card.
"""

from PySide6 import QtCore, QtWidgets


class StepIndicator(QtWidgets.QWidget):
    """Horizontal 1-2-3 progress stepper shown above the wizard's card.

    # OOP concept: INHERITANCE (framework classes)
    # -------------------------------------------------------------------
    # `StepIndicator` inherits from Qt's own `QtWidgets.QWidget`. This is
    # the same idea as the app's own class hierarchies (Panel, WizardStepPage)
    # but here the base class comes from the PySide6 framework: inheriting
    # from QWidget is what makes an ordinary Python object into something
    # Qt can lay out, show, and repaint.
    """

    STEP_LABELS = ["When", "Where", "Review"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._dots: list[QtWidgets.QLabel] = []
        self._names: list[QtWidgets.QLabel] = []

        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addStretch(1)

        for i, name in enumerate(self.STEP_LABELS):
            col = QtWidgets.QVBoxLayout()
            col.setSpacing(6)

            dot = QtWidgets.QLabel(str(i + 1))
            dot.setObjectName("stepDot")
            dot.setFixedSize(30, 30)
            dot.setAlignment(QtCore.Qt.AlignCenter)

            name_lbl = QtWidgets.QLabel(name)
            name_lbl.setObjectName("stepName")
            name_lbl.setAlignment(QtCore.Qt.AlignCenter)

            col.addWidget(dot, alignment=QtCore.Qt.AlignHCenter)
            col.addWidget(name_lbl)

            wrapper = QtWidgets.QWidget()
            wrapper.setLayout(col)
            row.addWidget(wrapper)

            self._dots.append(dot)
            self._names.append(name_lbl)

            if i < len(self.STEP_LABELS) - 1:
                connector = QtWidgets.QFrame()
                connector.setObjectName("stepConnector")
                connector.setFixedHeight(2)
                connector.setMinimumWidth(70)
                row.addWidget(connector)

        row.addStretch(1)

    def set_current(self, index: int) -> None:
        for i, (dot, name_lbl) in enumerate(zip(self._dots, self._names)):
            if i < index:
                state = "done"
            elif i == index:
                state = "active"
            else:
                state = "pending"
            for widget in (dot, name_lbl):
                widget.setProperty("stepState", state)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
