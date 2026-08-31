"""
popups/quick_settings_dialog.py
----------------------------------
QuickSettingsDialog - a small, toggleable popup that lives on top of the
MoonView screen. Unlike SetupWizard (the guided "When -> Where -> Review"
flow meant for the *first* setup) this dialog is for fast, one-off
tweaks once the simulation is already running: change just the date, or
just the time, or drag a new spot on the map - each change applies to
the simulation immediately, live, with no "Next" steps to click through.
"""

from __future__ import annotations

from datetime import datetime

from PySide6 import QtCore, QtWidgets

from ..models import DEFAULT_OBSERVATION_VALUES
from ..widgets import LocationPickerWidget


class QuickSettingsDialog(QtWidgets.QDialog):
    """
    A lightweight, non-modal "quick settings" popup for MoonView.

    # OOP concept: COMPOSITION + OBSERVER PATTERN (Qt Signals)
    # -----------------------------------------------------------------
    # This dialog HOLDS a LocationPickerWidget rather than reimplementing
    # map-drawing, location search or timezone lookup itself - the same
    # "has-a, delegates to" relationship MoonView has with
    # MoonCalculator/MoonFigureBuilder. It never touches MoonView's
    # internals directly either: it just emits `values_changed(dict)`
    # and lets whoever is listening (MoonView) decide what to do with
    # the new values - the same loosely-coupled Signal wiring used
    # throughout main_window.py.

    Every field applies its change immediately and independently: editing
    only the date emits an update with just the date field different from
    before; editing only the time does the same for time; nothing here
    requires touching (or re-validating) the fields the user didn't
    touch, unlike stepping through the full wizard.
    """

    values_changed = QtCore.Signal(dict)
    full_wizard_requested = QtCore.Signal()

    # Fixed width keeps this reading as a slim side panel docked to the
    # edge of the window rather than a big centered dialog; height is set
    # dynamically (see MoonView._position_quick_settings) to match
    # whatever room the app window actually has, so the footer buttons
    # are never pushed off the bottom of the screen.
    PANEL_WIDTH = 480

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Quick settings")
        self.setModal(False)
        # Qt.Tool keeps this as a lightweight utility popup (no taskbar
        # entry) that floats above MoonView instead of blocking it.
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)
        self.resize(self.PANEL_WIDTH, 640)

        self._values: dict[str, str] = dict(DEFAULT_OBSERVATION_VALUES)

        self._build_ui()
        self.set_values(self._values)

    # -- UI construction ------------------------------------------------------

    def _build_ui(self) -> None:
        # Header and footer sit OUTSIDE the scroll area and are always
        # fully visible; only the middle (date/time + location) scrolls,
        # so on a short screen the "Close" / "Open full wizard" buttons
        # stay reachable instead of being clipped off the bottom.
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_header())

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(20, 12, 20, 12)
        content_layout.setSpacing(14)
        content_layout.addWidget(self._build_datetime_group())
        content_layout.addWidget(self._build_location_group(), stretch=1)
        scroll.setWidget(content)
        outer.addWidget(scroll, stretch=1)

        outer.addWidget(self._build_footer())

    def _build_header(self) -> QtWidgets.QWidget:
        header = QtWidgets.QWidget()
        header.setObjectName("panelHeader")
        layout = QtWidgets.QVBoxLayout(header)
        layout.setContentsMargins(20, 18, 20, 12)
        layout.setSpacing(6)

        heading = QtWidgets.QLabel("⚡ Quick settings")
        heading.setObjectName("stepHeading")
        sub = QtWidgets.QLabel(
            "Change just the date, just the time, or the location — the "
            "simulation updates immediately, no need to step through setup."
        )
        sub.setObjectName("h2")
        sub.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(sub)
        return header

    def _build_footer(self) -> QtWidgets.QWidget:
        footer = QtWidgets.QWidget()
        footer.setObjectName("panelFooter")
        footer_layout = QtWidgets.QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 12, 20, 16)

        wizard_btn = QtWidgets.QPushButton("Open full setup wizard →")
        wizard_btn.setObjectName("ghost")
        wizard_btn.setCursor(QtCore.Qt.PointingHandCursor)
        wizard_btn.clicked.connect(self.full_wizard_requested.emit)
        footer_layout.addWidget(wizard_btn)
        footer_layout.addStretch(1)
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setObjectName("primary")
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.clicked.connect(self.hide)
        footer_layout.addWidget(close_btn)
        return footer

    def _build_datetime_group(self) -> QtWidgets.QGroupBox:
        group = QtWidgets.QGroupBox("DATE && TIME")
        grid = QtWidgets.QGridLayout(group)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(4)

        date_lbl = QtWidgets.QLabel("DATE")
        date_lbl.setObjectName("fieldLabel")
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")

        time_lbl = QtWidgets.QLabel("TIME")
        time_lbl.setObjectName("fieldLabel")
        self.time_edit = QtWidgets.QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")

        now_btn = QtWidgets.QPushButton("Use current date && time")
        now_btn.setObjectName("secondary")
        now_btn.setCursor(QtCore.Qt.PointingHandCursor)
        now_btn.clicked.connect(self._use_now)

        grid.addWidget(date_lbl, 0, 0)
        grid.addWidget(time_lbl, 0, 1)
        grid.addWidget(self.date_edit, 1, 0)
        grid.addWidget(self.time_edit, 1, 1)
        grid.addWidget(now_btn, 1, 2)
        grid.setColumnStretch(3, 1)

        self.date_edit.dateChanged.connect(self._on_date_changed)
        self.time_edit.timeChanged.connect(self._on_time_changed)
        return group

    def _build_location_group(self) -> QtWidgets.QGroupBox:
        group = QtWidgets.QGroupBox("LOCATION")
        layout = QtWidgets.QVBoxLayout(group)
        layout.setSpacing(10)

        hint = QtWidgets.QLabel(
            "Search for a country/city, click or drag on the map, or dial "
            "in exact coordinates."
        )
        hint.setObjectName("h2")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.location_picker = LocationPickerWidget()
        self.location_picker.values_changed.connect(self._on_location_changed)
        layout.addWidget(self.location_picker, stretch=1)
        return group

    # -- syncing from the outside world -----------------------------------

    def set_values(self, values: dict) -> None:
        """Repopulates every field from a values dict (date/time/tz/lat/lon/
        elev) without emitting values_changed - used whenever the popup is
        (re)opened so it always starts in sync with whatever MoonView is
        currently showing."""
        date_str = values.get("date", DEFAULT_OBSERVATION_VALUES["date"])
        try:
            year, month, day = (int(p) for p in date_str.split("-"))
            self.date_edit.setDate(QtCore.QDate(year, month, day))
        except ValueError:
            pass

        time_str = values.get("time", DEFAULT_OBSERVATION_VALUES["time"])
        try:
            parts = [int(p) for p in time_str.split(":")]
            while len(parts) < 3:
                parts.append(0)
            self.time_edit.setTime(QtCore.QTime(*parts))
        except ValueError:
            pass

        self.location_picker.set_values(values)
        self._values = dict(values)

    # -- date / time handlers -----------------------------------------------

    def _use_now(self) -> None:
        now = datetime.now()
        self.date_edit.setDate(QtCore.QDate(now.year, now.month, now.day))
        self.time_edit.setTime(QtCore.QTime(now.hour, now.minute, now.second))

    def _on_date_changed(self, qdate: QtCore.QDate) -> None:
        self._values["date"] = qdate.toString("yyyy-MM-dd")
        self.values_changed.emit({"date": self._values["date"]})

    def _on_time_changed(self, qtime: QtCore.QTime) -> None:
        self._values["time"] = qtime.toString("HH:mm:ss")
        self.values_changed.emit({"time": self._values["time"]})

    # -- location handlers -------------------------------------------------

    def _on_location_changed(self, location_values: dict) -> None:
        self._values.update(location_values)
        self.values_changed.emit(dict(location_values))
