"""
wizard/base_step_page.py
--------------------------
Common contract for the wizard's two data-entry steps (When / Where).
"""

from PySide6 import QtCore, QtWidgets

from ..theme import mark_field_error


class WizardStepPage(QtWidgets.QWidget):
    """
    Base class for a single page of the setup wizard that collects some
    fields and can validate them.

    # OOP concept: INHERITANCE + "TEMPLATE METHOD"-STYLE CONTRACT
    # -------------------------------------------------------------------
    # DateTimeStepPage and LocationStepPage both inherit from this class.
    # It cannot use Python's `abc.ABC` the way panels/base_panel.py does,
    # because PySide6's QWidget already has its own internal metaclass and
    # mixing it with ABCMeta would conflict - so instead the "this must be
    # overridden" contract is expressed the classic way: base methods
    # raise NotImplementedError, and every subclass provides its own
    # `values()`, `set_values()` and `validate()`. SetupWizard then calls
    # these same three method names on whichever step page is currently
    # showing, without needing to know which concrete step it is -
    # POLYMORPHISM again, just expressed with a lighter-weight contract.
    #
    # The shared bits that ARE common to every step - the error label and
    # the "clear the error as soon as the user edits a field" wiring - are
    # implemented once here and inherited, instead of being copy-pasted
    # into each step page.
    """

    advance_requested = QtCore.Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._all_edits: list[QtWidgets.QLineEdit] = []
        self.error_lbl = QtWidgets.QLabel("")
        self.error_lbl.setObjectName("statusLabel")
        self.error_lbl.setWordWrap(True)

    def _register_edit(self, edit: QtWidgets.QLineEdit) -> None:
        """Wires the "Enter submits" and "typing clears the error" behaviour
        that every field on every step page needs."""
        self._all_edits.append(edit)
        edit.returnPressed.connect(self.advance_requested.emit)
        edit.textChanged.connect(lambda _: self.show_error(None, None))

    def values(self) -> dict:
        raise NotImplementedError

    def set_values(self, values: dict) -> None:
        raise NotImplementedError

    def validate(self) -> tuple[QtWidgets.QLineEdit | None, str | None]:
        """Returns (invalid_field, message), or (None, None) if everything
        on this step is valid."""
        raise NotImplementedError

    def show_error(self, bad_field: QtWidgets.QLineEdit | None, message: str | None) -> None:
        self.error_lbl.setText(f"⚠ {message}" if message else "")
        for edit in self._all_edits:
            mark_field_error(edit, edit is bad_field)
