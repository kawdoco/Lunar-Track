"""
wizard/datetime_step_page.py
------------------------------
Wizard step 1 - choose the observation date, time and timezone.

Uses the same QDateEdit (with a calendar popup) / QTimeEdit / editable
timezone combo box that the Quick Settings popup already uses, instead
of three plain, freely-typed text fields the user had to get an exact
"YYYY-MM-DD" / "HH:MM:SS" format right for. That mismatch was the
biggest inconsistency in the app: the very first screen someone sees
looked and behaved like a rougher, more error-prone version of a
control the app already had a polished version of one screen later.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from PySide6 import QtCore, QtWidgets

from .base_step_page import WizardStepPage

_COMMON_TIMEZONES = [
    "UTC", "Asia/Colombo", "Asia/Kolkata", "Asia/Tokyo", "Asia/Shanghai",
    "Asia/Dubai", "Europe/London", "Europe/Paris", "Europe/Berlin",
    "Africa/Cairo", "Africa/Johannesburg", "America/New_York",
    "America/Chicago", "America/Los_Angeles", "America/Sao_Paulo",
    "Australia/Sydney", "Pacific/Auckland",
]


class DateTimeStepPage(WizardStepPage):
    """Wizard step 1 - choose the observation date, time and timezone.

    # OOP concept: INHERITANCE + METHOD OVERRIDING
    # -------------------------------------------------------------------
    # Inherits the error-label / edit-registration plumbing from
    # WizardStepPage, and overrides `values()`, `set_values()` and
    # `validate()` with logic specific to date/time/timezone fields.
    """

    QUICK_TIMEZONES = ["Asia/Colombo", "UTC", "Europe/London", "America/New_York", "Asia/Tokyo"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(18)

        heading = QtWidgets.QLabel("When do you want to look?")
        heading.setObjectName("stepHeading")
        sub = QtWidgets.QLabel("Pick a date, time and timezone to observe from.")
        sub.setObjectName("h2")
        outer.addWidget(heading)
        outer.addWidget(sub)

        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(4)

        date_lbl = QtWidgets.QLabel("DATE")
        date_lbl.setObjectName("fieldLabel")
        self.date_edit = QtWidgets.QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setMinimumWidth(150)

        time_lbl = QtWidgets.QLabel("TIME")
        time_lbl.setObjectName("fieldLabel")
        self.time_edit = QtWidgets.QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.time_edit.setMinimumWidth(130)

        tz_lbl = QtWidgets.QLabel("TIMEZONE (IANA)")
        tz_lbl.setObjectName("fieldLabel")
        self.tz_combo = QtWidgets.QComboBox()
        self.tz_combo.setEditable(True)
        self.tz_combo.addItems(_COMMON_TIMEZONES)
        self.tz_combo.setMinimumWidth(220)

        grid.addWidget(date_lbl, 0, 0)
        grid.addWidget(time_lbl, 0, 1)
        grid.addWidget(tz_lbl, 0, 2)
        grid.addWidget(self.date_edit, 1, 0)
        grid.addWidget(self.time_edit, 1, 1)
        grid.addWidget(self.tz_combo, 1, 2)
        grid.setColumnStretch(3, 1)
        outer.addLayout(grid)

        # Only the timezone field can hold an invalid value (any IANA
        # name can be typed) - the date/time pickers can't produce an
        # invalid date or time by construction, so only the timezone's
        # internal line edit needs the shared "Enter submits / typing
        # clears the error" wiring from WizardStepPage.
        self._register_edit(self.tz_combo.lineEdit())

        outer.addWidget(self.error_lbl)   # inherited from WizardStepPage

        quick_row = QtWidgets.QHBoxLayout()
        quick_row.setSpacing(8)
        now_btn = QtWidgets.QPushButton("Use current date && time")
        now_btn.setObjectName("secondary")
        now_btn.setCursor(QtCore.Qt.PointingHandCursor)
        now_btn.clicked.connect(self._use_now)
        quick_row.addWidget(now_btn)

        tz_row_lbl = QtWidgets.QLabel("Quick timezone:")
        tz_row_lbl.setObjectName("fieldLabel")
        quick_row.addWidget(tz_row_lbl)
        for name in self.QUICK_TIMEZONES:
            chip = QtWidgets.QPushButton(name.split("/")[-1].replace("_", " "))
            chip.setObjectName("chipButton")
            chip.setCursor(QtCore.Qt.PointingHandCursor)
            chip.clicked.connect(lambda _checked=False, n=name: self.tz_combo.setCurrentText(n))
            quick_row.addWidget(chip)
        quick_row.addStretch(1)
        outer.addLayout(quick_row)

        # A single trailing stretch keeps everything anchored near the
        # top of the card - any surplus height (the review/location
        # steps are taller) collects below, instead of being split
        # between a stretch placed BEFORE the heading too, which used
        # to push the whole step down and leave a large empty gap above
        # "When do you want to look?".
        outer.addStretch(1)

        self._use_now()

    def _use_now(self) -> None:
        now = datetime.now()
        self.date_edit.setDate(QtCore.QDate(now.year, now.month, now.day))
        self.time_edit.setTime(QtCore.QTime(now.hour, now.minute, now.second))

    def values(self) -> dict:
        return {
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "time": self.time_edit.time().toString("HH:mm:ss"),
            "tz": self.tz_combo.currentText().strip(),
        }

    def set_values(self, values: dict) -> None:
        date_str = values.get("date", "")
        try:
            year, month, day = (int(p) for p in date_str.split("-"))
            self.date_edit.setDate(QtCore.QDate(year, month, day))
        except (ValueError, TypeError):
            pass

        time_str = values.get("time", "")
        try:
            parts = [int(p) for p in time_str.split(":")]
            while len(parts) < 3:
                parts.append(0)
            self.time_edit.setTime(QtCore.QTime(*parts[:3]))
        except (ValueError, TypeError):
            pass

        tz = values.get("tz", "")
        if tz:
            self.tz_combo.setCurrentText(tz)

    def validate(self) -> tuple[QtWidgets.QLineEdit | None, str | None]:
        # Date and time can no longer be invalid - QDateEdit/QTimeEdit
        # only ever hold a real date/time. Only the freely-typed
        # timezone still needs checking.
        tz = self.tz_combo.currentText().strip()
        if not tz:
            return self.tz_combo.lineEdit(), "Please enter a timezone."
        try:
            ZoneInfo(tz)
        except Exception:
            return self.tz_combo.lineEdit(), f"Unknown timezone: '{tz}'."
        return None, None
