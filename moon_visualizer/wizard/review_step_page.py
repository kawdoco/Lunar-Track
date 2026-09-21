"""
wizard/review_step_page.py
-----------------------------
Wizard step 3 - a read-only summary of everything chosen so far.
"""

from PySide6 import QtWidgets


class ReviewStepPage(QtWidgets.QWidget):
    """Wizard step 3 - a read-only summary of everything chosen so far.

    # OOP concept: composition over forced inheritance
    # -------------------------------------------------------------------
    # Unlike DateTimeStepPage/LocationStepPage, this step doesn't collect
    # or validate input, so it deliberately does NOT inherit from
    # WizardStepPage - inheriting just to get an error label it would
    # never use would be a poor fit ("is-a" would be false here). It only
    # inherits directly from QWidget, which is the honest relationship.
    """

    WHEN_ROWS = [("date", "Date"), ("time", "Time"), ("tz", "Timezone")]
    WHERE_ROWS = [("lat", "Latitude"), ("lon", "Longitude"), ("elev", "Elevation")]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(20)

        heading = QtWidgets.QLabel("Everything look right?")
        heading.setObjectName("stepHeading")
        sub = QtWidgets.QLabel("Check the details below, then show the Moon.")
        sub.setObjectName("h2")
        outer.addWidget(heading)
        outer.addWidget(sub)

        # Two side-by-side "WHEN" / "WHERE" sections instead of one long
        # flat list - mirrors the wizard's own step names, and each
        # section's value column sits directly beside its labels instead
        # of being stretched all the way to the far edge of the card.
        sections_row = QtWidgets.QHBoxLayout()
        sections_row.setSpacing(56)
        self._value_labels: dict[str, QtWidgets.QLabel] = {}
        sections_row.addLayout(self._build_section("WHEN", self.WHEN_ROWS))
        sections_row.addLayout(self._build_section("WHERE", self.WHERE_ROWS))
        sections_row.addStretch(1)
        outer.addLayout(sections_row)

        # A single trailing stretch - any surplus card height (this step
        # is naturally shorter than the location step) collects below
        # the content instead of being split between a stretch placed
        # BEFORE the heading too, which used to push everything down and
        # leave a large empty gap above "Everything look right?".
        outer.addStretch(1)

    def _build_section(self, title: str, rows: list[tuple[str, str]]) -> QtWidgets.QVBoxLayout:
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(12)

        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setObjectName("sectionTitle")
        col.addWidget(title_lbl)

        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(10)
        # Only the value column should absorb any extra width - without
        # this, Qt splits surplus space evenly across BOTH columns by
        # default, which is what used to push the values far away from
        # their labels with a huge, ugly gap in between.
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        for row, (key, label_text) in enumerate(rows):
            lbl = QtWidgets.QLabel(label_text)
            lbl.setObjectName("fieldLabel")
            val = QtWidgets.QLabel("—")
            val.setObjectName("reviewValue")
            grid.addWidget(lbl, row, 0)
            grid.addWidget(val, row, 1)
            self._value_labels[key] = val

        col.addLayout(grid)
        return col

    def set_summary(self, values: dict) -> None:
        display = {
            "date": values.get("date") or "—",
            "time": values.get("time") or "—",
            "tz": values.get("tz") or "—",
            "lat": f"{values.get('lat', '—')}°",
            "lon": f"{values.get('lon', '—')}°",
            "elev": f"{values.get('elev') or '0'} m",
        }
        for key, lbl in self._value_labels.items():
            lbl.setText(display.get(key, "—"))
