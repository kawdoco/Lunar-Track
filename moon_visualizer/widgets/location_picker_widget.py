"""
widgets/location_picker_widget.py
------------------------------------
LocationPickerWidget - the ONE place that knows how to pick an observer
location (search box + map + lat/lon/elevation + timezone auto-detect).

This used to be built twice, slightly differently: once (well) inside
QuickSettingsDialog, and once (as a plainer set of text fields, with no
map) inside the wizard's LocationStepPage. Both now embed this same
widget instead, so "quick settings" and "first-time setup" look and
behave identically for location - one professional, consistent piece of
UI instead of two out-of-sync ones.
"""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from ..geo import ALL_LOCATIONS, FAVORITE_LOCATIONS, TimezoneResolver, find_by_name
from .flow_layout import FlowLayout
from .world_map_widget import WorldMapWidget

# A short list of common zones shown in the dropdown; the field stays a
# free-typed, editable combo box so ANY valid IANA name still works.
_COMMON_TIMEZONES = [
    "UTC", "Asia/Colombo", "Asia/Kolkata", "Asia/Tokyo", "Asia/Shanghai",
    "Asia/Dubai", "Europe/London", "Europe/Paris", "Europe/Berlin",
    "Africa/Cairo", "Africa/Johannesburg", "America/New_York",
    "America/Chicago", "America/Los_Angeles", "America/Sao_Paulo",
    "Australia/Sydney", "Pacific/Auckland",
]

_ALL_LOCATION_NAMES = [loc.name for loc in ALL_LOCATIONS]


class LocationPickerWidget(QtWidgets.QWidget):
    """
    Composite "where on Earth" input: type a country/city name to jump
    straight to it, click/drag on the map for a rough pick, or dial in
    exact latitude/longitude/elevation - all three stay in sync with
    each other, and the timezone field follows automatically unless the
    user has typed one in manually.

    # OOP concept: COMPOSITION + OBSERVER PATTERN (Qt Signals)
    # -----------------------------------------------------------------
    # This widget HOLDS a WorldMapWidget and a TimezoneResolver rather
    # than reimplementing map-drawing or timezone lookup itself. It never
    # reaches into whoever is using it (QuickSettingsDialog,
    # LocationStepPage) - it just emits `values_changed(dict)` and lets
    # the caller decide what to do with the new lat/lon/elev/tz values,
    # the same loosely-coupled Signal wiring used throughout the app.
    """

    values_changed = QtCore.Signal(dict)

    def __init__(self, parent=None, wide: bool = False) -> None:
        """`wide=True` switches to a side-by-side layout (map on the left,
        a compact search/coordinates/timezone form on the right) instead
        of the original everything-stacked-in-one-column arrangement.

        The stacked layout works fine at the narrow, fixed width the
        Quick Settings popup uses (`PANEL_WIDTH = 480`) - there just
        isn't room beside the map for anything else there. But the setup
        wizard's location step has the whole width of the window to
        work with, and stacking every row there too was the bug behind
        the map rendering as a tiny letterboxed strip with acres of dead
        space on either side: the map is aspect-locked to 2:1, so
        squeezing it into a short *height* (because four other full-width
        rows were stacked below it, each claiming their own height)
        capped its width too, no matter how wide the window was. Putting
        the form beside the map instead of below it gives the map the
        *height* it needs to actually use the available width.
        """
        super().__init__(parent)
        self._wide = wide
        self._tz_resolver = TimezoneResolver()
        # Guards against feedback loops while this widget updates its OWN
        # widgets programmatically - only user-driven edits should
        # re-emit values_changed.
        self._suppress_emit = False
        # Dragging on the map fires a new (lat, lon) on every single
        # mouse-move event - tens of times a second. Re-resolving and
        # repainting the timezone combo box that often (it's a styled,
        # rounded-border widget, which is expensive to redraw) is what
        # was leaving stale/overlapping pixels behind on Windows and
        # made the field look garbled: the paint for one update hadn't
        # finished before the next one landed. This timer coalesces
        # those bursts into a single update ~70ms after the pointer
        # settles, instead of resolving on every intermediate point.
        self._tz_debounce = QtCore.QTimer(self)
        self._tz_debounce.setSingleShot(True)
        self._tz_debounce.setInterval(70)
        self._tz_debounce.timeout.connect(self._resolve_pending_tz)
        self._pending_latlon: tuple[float, float] | None = None
        self._values: dict[str, str] = {"lat": "6.9271", "lon": "79.8612", "elev": "0", "tz": "UTC"}

        self._build_ui()

    # -- UI construction ------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(14 if self._wide else 10)

        outer.addLayout(self._build_search_row())

        self.map_widget = WorldMapWidget()

        if self._wide:
            # Map on the left (gets the lion's share of both the width
            # AND the height, since it's no longer squeezed underneath
            # a stack of other full-width rows), a compact form column
            # on the right.
            self.map_widget.setMinimumSize(420, 300)
            split_row = QtWidgets.QHBoxLayout()
            split_row.setSpacing(28)
            split_row.addWidget(self.map_widget, stretch=1)

            form_col = QtWidgets.QVBoxLayout()
            form_col.setSpacing(16)
            form_col.addLayout(self._build_coords_grid())
            form_col.addLayout(self._build_favorites_flow())
            form_col.addLayout(self._build_timezone_col())
            form_col.addStretch(1)

            form_widget = QtWidgets.QWidget()
            form_widget.setLayout(form_col)
            form_widget.setMaximumWidth(340)
            split_row.addWidget(form_widget, stretch=0)

            outer.addLayout(split_row, stretch=1)
        else:
            outer.addWidget(self.map_widget, stretch=1)
            outer.addLayout(self._build_coords_grid())
            outer.addLayout(self._build_favorites_row())
            outer.addLayout(self._build_timezone_row())

        self.map_widget.location_picked.connect(self._on_map_picked)
        self.map_widget.preset_picked.connect(self._on_named_picked)
        self.lat_spin.valueChanged.connect(self._on_lat_spin_changed)
        self.lon_spin.valueChanged.connect(self._on_lon_spin_changed)
        self.elev_spin.valueChanged.connect(self._on_elev_changed)
        self.auto_tz_check.toggled.connect(self._on_auto_tz_toggled)
        self.tz_combo.activated.connect(self._on_tz_selected)
        self.tz_combo.lineEdit().editingFinished.connect(self._on_tz_edited)
        self._update_precision_note()

        self.set_values(self._values)

    def _build_search_row(self) -> QtWidgets.QVBoxLayout:
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(4)
        lbl = QtWidgets.QLabel("SEARCH ANY LOCATION")
        lbl.setObjectName("fieldLabel")
        col.addWidget(lbl)

        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Type a country or city, e.g. \"Nepal\", \"Tokyo\"…")
        completer = QtWidgets.QCompleter(_ALL_LOCATION_NAMES, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.search_edit.setCompleter(completer)
        completer.activated[str].connect(self._on_search_chosen)
        self.search_edit.returnPressed.connect(self._on_search_return)
        col.addWidget(self.search_edit)
        return col

    def _build_coords_grid(self) -> QtWidgets.QGridLayout:
        """Builds the lat/lon/elevation spin boxes - shared by both the
        stacked (narrow) and side-by-side (wide) layouts, since the
        fields themselves (self.lat_spin etc.) are identical either way,
        only their surrounding arrangement differs."""
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(4)
        self.lat_spin = self._coord_spin(grid, 0, "LATITUDE (°)", -90.0, 90.0)
        self.lon_spin = self._coord_spin(grid, 1, "LONGITUDE (°)", -180.0, 180.0)
        self.elev_spin = self._coord_spin(grid, 2, "ELEVATION (m)", -500.0, 9000.0, decimals=0)
        return grid

    def _build_favorites_row(self) -> QtWidgets.QHBoxLayout:
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(8)
        lbl = QtWidgets.QLabel("Quick picks:")
        lbl.setObjectName("fieldLabel")
        row.addWidget(lbl)
        for loc in FAVORITE_LOCATIONS:
            row.addWidget(self._favorite_chip(loc))
        row.addStretch(1)
        return row

    def _build_favorites_flow(self) -> QtWidgets.QVBoxLayout:
        """Same quick-pick chips as `_build_favorites_row`, but wrapped
        in a FlowLayout instead of a single QHBoxLayout - needed because
        the wide layout's form column is only ~300px wide, nowhere near
        enough to fit all six chips on one line without either clipping
        them or squashing them unreadably thin."""
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(4)
        lbl = QtWidgets.QLabel("QUICK PICKS")
        lbl.setObjectName("fieldLabel")
        col.addWidget(lbl)

        flow_widget = QtWidgets.QWidget()
        flow = FlowLayout(flow_widget, margin=0, h_spacing=8, v_spacing=8)
        for loc in FAVORITE_LOCATIONS:
            flow.addWidget(self._favorite_chip(loc))
        col.addWidget(flow_widget)
        return col

    def _favorite_chip(self, loc: WorldLocation) -> QtWidgets.QPushButton:
        chip = QtWidgets.QPushButton(loc.name.split(",")[0])
        chip.setObjectName("chipButton")
        chip.setCursor(QtCore.Qt.PointingHandCursor)
        chip.clicked.connect(lambda _checked=False, l=loc: self._on_named_picked(
            l.name, l.latitude_deg, l.longitude_deg, l.timezone))
        return chip

    def _build_timezone_row(self) -> QtWidgets.QVBoxLayout:
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(6)

        tz_row = QtWidgets.QHBoxLayout()
        tz_row.setSpacing(10)
        self.auto_tz_check = QtWidgets.QCheckBox("Auto-detect timezone from location")
        self.auto_tz_check.setChecked(True)
        tz_lbl = QtWidgets.QLabel("TIMEZONE")
        tz_lbl.setObjectName("fieldLabel")
        self.tz_combo = QtWidgets.QComboBox()
        self.tz_combo.setEditable(True)
        self.tz_combo.addItems(_COMMON_TIMEZONES)
        tz_row.addWidget(self.auto_tz_check)
        tz_row.addStretch(1)
        tz_row.addWidget(tz_lbl)
        tz_row.addWidget(self.tz_combo)
        col.addLayout(tz_row)

        self.precision_note = QtWidgets.QLabel("")
        self.precision_note.setObjectName("statusLabel")
        self.precision_note.setWordWrap(True)
        col.addWidget(self.precision_note)
        return col

    def _build_timezone_col(self) -> QtWidgets.QVBoxLayout:
        """Same timezone controls as `_build_timezone_row`, but stacked
        vertically (checkbox, then label+combo, then the precision
        note) instead of packed into one wide row - the wide layout's
        ~300px form column has no room to lay the checkbox and the combo
        side by side without truncating the checkbox's own label."""
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(6)

        self.auto_tz_check = QtWidgets.QCheckBox("Auto-detect timezone")
        self.auto_tz_check.setChecked(True)
        col.addWidget(self.auto_tz_check)

        tz_lbl = QtWidgets.QLabel("TIMEZONE")
        tz_lbl.setObjectName("fieldLabel")
        col.addWidget(tz_lbl)
        self.tz_combo = QtWidgets.QComboBox()
        self.tz_combo.setEditable(True)
        self.tz_combo.addItems(_COMMON_TIMEZONES)
        # Long zone names (e.g. "Australia/Sydney", "America/Los_Angeles")
        # need more room than the box would otherwise claim by default.
        self.tz_combo.setMinimumWidth(180)
        col.addWidget(self.tz_combo)

        self.precision_note = QtWidgets.QLabel("")
        self.precision_note.setObjectName("statusLabel")
        self.precision_note.setWordWrap(True)
        col.addWidget(self.precision_note)
        return col

    def _update_precision_note(self) -> None:
        """The 'install timezonefinder for precise auto-detection' warning
        only makes sense while auto-detect is actually turned on - once
        the user has picked a timezone manually (which switches
        auto-detect off), that warning no longer applies to anything and
        was confusingly left showing regardless of state before."""
        show_warning = self.auto_tz_check.isChecked() and not self._tz_resolver.is_precise
        self.precision_note.setText(
            "⚠ Install the optional 'timezonefinder' package for precise "
            "auto-detected timezones (currently using a rough longitude-only estimate)."
            if show_warning else ""
        )

    def _coord_spin(
        self,
        grid: QtWidgets.QGridLayout,
        col: int,
        label_text: str,
        minimum: float,
        maximum: float,
        decimals: int = 4,
    ) -> QtWidgets.QDoubleSpinBox:
        lbl = QtWidgets.QLabel(label_text)
        lbl.setObjectName("fieldLabel")
        spin = QtWidgets.QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setDecimals(decimals)
        grid.addWidget(lbl, 0, col)
        grid.addWidget(spin, 1, col)
        return spin

    # -- public API -----------------------------------------------------------

    def values(self) -> dict:
        return dict(self._values)

    def set_values(self, values: dict) -> None:
        """Repopulates every field from a values dict (lat/lon/elev/tz)
        without emitting values_changed - used whenever the caller wants
        to (re)sync this widget with an outside source of truth."""
        self._suppress_emit = True
        try:
            try:
                lat = float(values.get("lat", 0.0))
                lon = float(values.get("lon", 0.0))
                elev = float(values.get("elev") or 0.0)
            except (TypeError, ValueError):
                lat, lon, elev = 0.0, 0.0, 0.0
            self.lat_spin.setValue(lat)
            self.lon_spin.setValue(lon)
            self.elev_spin.setValue(elev)
            self.map_widget.set_location(lat, lon)
            self.search_edit.clear()

            self._set_tz_text(values.get("tz", "UTC"))
        finally:
            self._suppress_emit = False
        self._values = {
            "lat": f"{lat:.4f}",
            "lon": f"{lon:.4f}",
            "elev": f"{elev:g}",
            "tz": values.get("tz", "UTC"),
        }

    # -- search handlers -----------------------------------------------------

    def _on_search_chosen(self, name: str) -> None:
        loc = find_by_name(name)
        if loc is not None:
            self._on_named_picked(loc.name, loc.latitude_deg, loc.longitude_deg, loc.timezone)

    def _on_search_return(self) -> None:
        text = self.search_edit.text().strip()
        if not text:
            return
        loc = find_by_name(text)
        if loc is None:
            # Fall back to the first name that CONTAINS what was typed,
            # so "nepal" (lowercase, no exact-case match) still works
            # even without opening the completer popup first.
            needle = text.casefold()
            for candidate in _ALL_LOCATION_NAMES:
                if needle in candidate.casefold():
                    loc = find_by_name(candidate)
                    break
        if loc is not None:
            self._on_named_picked(loc.name, loc.latitude_deg, loc.longitude_deg, loc.timezone)

    # -- location handlers -------------------------------------------------

    def _on_map_picked(self, lat: float, lon: float) -> None:
        self._apply_location(lat, lon)

    def _on_named_picked(self, name: str, lat: float, lon: float, tz: str) -> None:
        self._apply_location(lat, lon, preset_tz=tz, label=name)

    def _on_lat_spin_changed(self, value: float) -> None:
        if self._suppress_emit:
            return
        self._apply_location(value, self.lon_spin.value())

    def _on_lon_spin_changed(self, value: float) -> None:
        if self._suppress_emit:
            return
        self._apply_location(self.lat_spin.value(), value)

    def _on_elev_changed(self, value: float) -> None:
        if self._suppress_emit:
            return
        self._values["elev"] = f"{value:g}"
        self._emit()

    def _apply_location(self, lat: float, lon: float, preset_tz: str | None = None, label: str = "") -> None:
        self._suppress_emit = True
        try:
            self.lat_spin.setValue(lat)
            self.lon_spin.setValue(lon)
            self.map_widget.set_location(lat, lon, label=label)
            self.search_edit.setText(label)
            self._values["lat"] = f"{lat:.4f}"
            self._values["lon"] = f"{lon:.4f}"
            if self.auto_tz_check.isChecked():
                # Location-driven timezone sync: whenever the observer
                # moves (map click/drag, spin box, search pick, or a
                # favourite chip), the timezone field follows
                # automatically instead of being left stale.
                if preset_tz:
                    # A single discrete pick (favourite chip, search,
                    # named preset on the map) - resolve immediately,
                    # there's no flood of events to coalesce here.
                    self._tz_debounce.stop()
                    self._pending_latlon = None
                    self._set_tz_text(preset_tz)
                    self._values["tz"] = preset_tz
                else:
                    # Map drag / spin box nudge - could be one of many
                    # rapid-fire updates, so debounce the actual resolve
                    # + repaint (see _tz_debounce above).
                    self._pending_latlon = (lat, lon)
                    self._tz_debounce.start()
        finally:
            self._suppress_emit = False
        self._emit()

    def _resolve_pending_tz(self) -> None:
        if self._pending_latlon is None:
            return
        lat, lon = self._pending_latlon
        self._pending_latlon = None
        tz = self._tz_resolver.resolve(lat, lon)
        if not tz:
            return
        self._suppress_emit = True
        try:
            self._set_tz_text(tz)
        finally:
            self._suppress_emit = False
        self._values["tz"] = tz
        self._emit()

    # -- timezone handlers ---------------------------------------------------

    def _on_auto_tz_toggled(self, checked: bool) -> None:
        self._update_precision_note()
        if self._suppress_emit or not checked:
            return
        tz = self._tz_resolver.resolve(self.lat_spin.value(), self.lon_spin.value())
        if tz:
            self._suppress_emit = True
            try:
                self._set_tz_text(tz)
            finally:
                self._suppress_emit = False
            self._values["tz"] = tz
            self._emit()

    def _on_tz_selected(self, _index: int) -> None:
        self._apply_manual_tz(self.tz_combo.currentText())

    def _on_tz_edited(self) -> None:
        self._apply_manual_tz(self.tz_combo.currentText())

    def _apply_manual_tz(self, text: str) -> None:
        if self._suppress_emit:
            return
        text = text.strip()
        if not text or text == self._values.get("tz"):
            return
        # The user is now driving the timezone directly - stop overriding
        # it automatically every time the location changes.
        if self.auto_tz_check.isChecked():
            self.auto_tz_check.blockSignals(True)
            self.auto_tz_check.setChecked(False)
            self.auto_tz_check.blockSignals(False)
            self._update_precision_note()
        self._values["tz"] = text
        self._emit()

    def _set_tz_text(self, tz: str) -> None:
        self.tz_combo.blockSignals(True)
        self.tz_combo.setCurrentText(tz)
        self.tz_combo.blockSignals(False)
        # Force a full, clean repaint rather than relying on Qt's normal
        # partial-invalidation - repeated programmatic text changes were
        # the thing leaving stale/overlapping pixels in this box (see
        # the debounce note in __init__), so make sure every text swap
        # actually redraws the whole widget from scratch.
        self.tz_combo.update()
        line_edit = self.tz_combo.lineEdit()
        if line_edit is not None:
            line_edit.update()

    # -- emitting -----------------------------------------------------------

    def _emit(self) -> None:
        if not self._suppress_emit:
            self.values_changed.emit(dict(self._values))
