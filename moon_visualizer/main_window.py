"""
main_window.py
----------------
The top-level QMainWindow: owns a QStackedWidget holding Home / Wizard /
MoonView, and wires their signals together.
"""

from PySide6 import QtWidgets

from .astronomy import MoonCalculator
from .models import DEFAULT_OBSERVATION_VALUES
from .views import HomePage, MoonView
from .wizard import SetupWizard


class MainWindow(QtWidgets.QMainWindow):
    """
    The application's main window.

    # OOP concept: COMPOSITION AS THE APPLICATION'S "GLUE"
    # -------------------------------------------------------------------
    # MainWindow doesn't inherit from HomePage, SetupWizard or MoonView -
    # it HOLDS one instance of each (composition) inside a QStackedWidget,
    # and its whole job is to listen to their Signals and tell the stack
    # which page to show next. Every other class in this app (Theme,
    # domain models, astronomy classes, panels, wizard steps, views) is
    # ultimately composed together here, at the top of the object graph -
    # this is the "composition root" of the whole OOP design.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Moon Visualizer")
        self.resize(1560, 850)
        # Below this, the wizard's cards and the map/form split no longer
        # have room to lay out sensibly - better to stay usable at a
        # slightly bigger minimum than to let the window shrink into a
        # squashed, overlapping mess.
        self.setMinimumSize(1180, 720)

        self._calculator = MoonCalculator()
        self._last_values: dict = dict(DEFAULT_OBSERVATION_VALUES)
        self._editing_from_moon_view = False

        self.stack = QtWidgets.QStackedWidget()
        self.home_page = HomePage()
        self.wizard = SetupWizard()
        self.moon_view = MoonView(self._calculator)

        self.stack.addWidget(self.home_page)   # index 0
        self.stack.addWidget(self.wizard)      # index 1
        self.stack.addWidget(self.moon_view)   # index 2
        self.setCentralWidget(self.stack)

        self.home_page.setup_requested.connect(self._start_wizard)
        self.home_page.quick_launch_requested.connect(self._quick_launch)
        self.wizard.completed.connect(self._wizard_completed)
        self.wizard.cancelled.connect(self._wizard_cancelled)
        self.moon_view.home_requested.connect(self._open_home)
        self.moon_view.edit_requested.connect(self._edit_settings)

    def _start_wizard(self) -> None:
        self._editing_from_moon_view = False
        self.wizard.start(self._last_values)
        self.stack.setCurrentWidget(self.wizard)

    def _quick_launch(self) -> None:
        self._last_values = dict(DEFAULT_OBSERVATION_VALUES)
        self.moon_view.apply_values(self._last_values)
        self.stack.setCurrentWidget(self.moon_view)

    def _edit_settings(self) -> None:
        self._editing_from_moon_view = True
        self.wizard.start(self._last_values)
        self.stack.setCurrentWidget(self.wizard)

    def _wizard_completed(self, values: dict) -> None:
        self._last_values = values
        self.moon_view.apply_values(values)
        self.stack.setCurrentWidget(self.moon_view)

    def _wizard_cancelled(self) -> None:
        if self._editing_from_moon_view:
            self.stack.setCurrentWidget(self.moon_view)
        else:
            self.stack.setCurrentWidget(self.home_page)

    def _open_home(self) -> None:
        self.stack.setCurrentWidget(self.home_page)
