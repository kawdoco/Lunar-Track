"""
wizard/location_step_page.py
------------------------------
Wizard step 2 - choose the observer's location on Earth.

This now embeds the same LocationPickerWidget used by the Quick Settings
popup (search box + map + lat/lon/elevation + timezone auto-detect)
instead of a separate, plainer set of text fields - so the very first
time someone sets up the app, they get the same professional, easy way
to find a location as they do later when tweaking it.
"""

from PySide6 import QtCore, QtWidgets

from ..widgets import LocationPickerWidget
from .base_step_page import WizardStepPage


class LocationStepPage(WizardStepPage):
    """Wizard step 2 - choose the observer's location on Earth.

    # OOP concept: INHERITANCE + METHOD OVERRIDING
    # -------------------------------------------------------------------
    # Same base class as DateTimeStepPage, but this subclass overrides the
    # same three method names with logic for latitude/longitude/elevation
    # instead - each subclass fills in the "how" for its own fields while
    # SetupWizard keeps calling the shared "what" (values/set_values/validate).
    #
    # # OOP concept: COMPOSITION
    # -------------------------------------------------------------------
    # This step doesn't paint a map or resolve timezones itself - it HOLDS
    # a LocationPickerWidget and delegates all of that to it, exactly the
    # way QuickSettingsDialog does. Two different screens sharing one
    # underlying widget instead of two near-duplicate implementations.
    """

    # Emits an IANA timezone name whenever the location picker resolves
    # one for the current point (via search, map click/drag, or a
    # favourite) - SetupWizard forwards this straight into step 1's
    # timezone field, the same "location suggests the timezone" behaviour
    # Quick Settings already had.
    timezone_suggested = QtCore.Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(16)

        heading = QtWidgets.QLabel("Where are you observing from?")
        heading.setObjectName("stepHeading")
        sub = QtWidgets.QLabel(
            "Search for a country or city, click/drag on the map, or enter "
            "exact coordinates."
        )
        sub.setObjectName("h2")
        outer.addWidget(heading)
        outer.addWidget(sub)

        self.picker = LocationPickerWidget(wide=True)
        self.picker.values_changed.connect(self._on_picker_changed)
        outer.addWidget(self.picker, stretch=1)

        outer.addWidget(self.error_lbl)

    # -- WizardStepPage contract ------------------------------------------

    def values(self) -> dict:
        # Deliberately excludes "tz" - the timezone field lives on step 1
        # only; this step just *suggests* one via `timezone_suggested`
        # whenever the location changes, without overwriting whatever the
        # user may have typed there manually.
        picked = self.picker.values()
        return {"lat": picked["lat"], "lon": picked["lon"], "elev": picked["elev"]}

    def set_values(self, values: dict) -> None:
        self.picker.set_values(values)

    def validate(self) -> tuple[QtWidgets.QLineEdit | None, str | None]:
        # Every field here is a spin box or a map pick, both range-limited
        # by construction (lat/-90..90, lon/-180..180) - there is no
        # invalid state left to catch, unlike the old free-typed fields.
        return None, None

    # -- picker sync -----------------------------------------------------

    def _on_picker_changed(self, location_values: dict) -> None:
        tz = location_values.get("tz")
        if tz:
            self.timezone_suggested.emit(tz)
