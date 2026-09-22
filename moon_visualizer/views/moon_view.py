"""
views/moon_view.py
--------------------
The visualizer screen itself: summary chip + time-lapse bar + the rendered
Matplotlib figure.
"""

from datetime import datetime, timedelta

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6 import QtCore, QtWidgets

from ..theme import Theme
from ..models import ObservationMoment, ObserverLocation, MoonObservationResult, DEFAULT_OBSERVATION_VALUES
from ..astronomy import MoonCalculator
from ..panels import MoonFigureBuilder
from ..popups import QuickSettingsDialog


class MoonView(QtWidgets.QWidget):
    """The Moon visualizer's main view. All the observation settings now
    live in the SetupWizard; this screen just shows a compact summary chip
    (with an Edit button to reopen the wizard) plus the time-lapse bar and
    the rendered figure, which now gets almost the whole screen.

    # OOP concept: COMPOSITION (a class built from other classes)
    # -------------------------------------------------------------------
    # MoonView HOLDS a MoonCalculator and a MoonFigureBuilder, handed in
    # (the calculator) or created (the figure builder) at construction
    # time, and delegates the actual astronomy/drawing work to them. This
    # view's own job is narrow: read the UI's current inputs, ask its
    # collaborators to do the heavy lifting, and place the resulting
    # Matplotlib canvas on screen.
    """

    home_requested = QtCore.Signal()
    edit_requested = QtCore.Signal()

    # step-size choices for time-lapse mode: label -> timedelta
    STEP_CHOICES = [
        ("10 minutes / tick", timedelta(minutes=10)),
        ("1 hour / tick", timedelta(hours=1)),
        ("6 hours / tick", timedelta(hours=6)),
        ("1 day / tick", timedelta(days=1)),
        ("7 days / tick", timedelta(days=7)),
    ]

    # speed choices: label -> duration (ms) to sweep through ONE full step
    # (lower = faster). This used to be the raw QTimer interval that fired a
    # full jump every tick -- now it's the length of the smooth transition.
    SPEED_CHOICES = [
        ("Slow", 1400),
        ("Normal", 700),
        ("Fast", 300),
        ("Very fast", 90),
    ]

    # Fixed-rate repaint tick for the animation itself (~33 fps). This is
    # independent of playback speed -- speed only changes how long it takes
    # to sweep through one step, not how often we repaint.
    _FRAME_INTERVAL_MS = 30

    def __init__(self, calculator: MoonCalculator, parent=None) -> None:
        super().__init__(parent)
        self._calculator = calculator
        self._figure_builder = MoonFigureBuilder()
        self._values: dict[str, str] = dict(DEFAULT_OBSERVATION_VALUES)
        self._canvas: FigureCanvasQTAgg | None = None
        self._playing = False

        # Time-lapse now animates THROUGH each step instead of snapping to
        # it: a fast, fixed-rate frame timer repaints in-between instants
        # while `_step_elapsed` tracks progress across the current step, so
        # the Moon disk, sky position, clock hands and calendar highlight
        # all sweep smoothly instead of jumping once per tick.
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(self._FRAME_INTERVAL_MS)
        self._timer.timeout.connect(self._on_frame)
        self._step_elapsed = QtCore.QElapsedTimer()
        self._step_start_local: datetime | None = None
        self._step_duration_ms: int = self.SPEED_CHOICES[1][1]

        # The quick-settings popup is created once and just shown/hidden
        # (toggled) from here on, instead of being rebuilt every time -
        # its own `set_values()` keeps it in sync each time it reopens.
        self._quick_settings = QuickSettingsDialog(self)
        self._quick_settings.values_changed.connect(self._on_quick_values_changed)
        self._quick_settings.full_wizard_requested.connect(self._request_edit)

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 16, 24, 16)
        outer.setSpacing(10)

        # ---- header: home | title | summary chip + edit --------------------
        header = QtWidgets.QHBoxLayout()
        header.setSpacing(12)
        home_btn = QtWidgets.QPushButton("←  Home")
        home_btn.setObjectName("ghost")
        home_btn.setCursor(QtCore.Qt.PointingHandCursor)
        home_btn.clicked.connect(self._go_home)
        title = QtWidgets.QLabel("🌙 Moon Visualizer")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Theme.TEXT};")

        self._summary_chip = QtWidgets.QLabel("")
        self._summary_chip.setObjectName("summaryChip")
        quick_btn = QtWidgets.QPushButton("⚡  Quick settings")
        quick_btn.setObjectName("secondary")
        quick_btn.setCursor(QtCore.Qt.PointingHandCursor)
        quick_btn.clicked.connect(self._toggle_quick_settings)
        edit_btn = QtWidgets.QPushButton("✎  Full setup")
        edit_btn.setObjectName("secondary")
        edit_btn.setCursor(QtCore.Qt.PointingHandCursor)
        edit_btn.clicked.connect(self._request_edit)

        header.addWidget(home_btn)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self._summary_chip)
        header.addWidget(quick_btn)
        header.addWidget(edit_btn)
        outer.addLayout(header)

        # ---- compact time-lapse bar -----------------------------------------
        lapse_row = QtWidgets.QHBoxLayout()
        lapse_row.setSpacing(12)

        self._play_btn = QtWidgets.QPushButton("▶")
        self._play_btn.setObjectName("playButton")
        self._play_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self._play_btn.clicked.connect(self._toggle_play)
        lapse_row.addWidget(self._play_btn)

        step_lbl = QtWidgets.QLabel("STEP")
        step_lbl.setObjectName("fieldLabel")
        self._step_combo = QtWidgets.QComboBox()
        for label, _ in self.STEP_CHOICES:
            self._step_combo.addItem(label)
        self._step_combo.setCurrentIndex(1)
        lapse_row.addWidget(step_lbl)
        lapse_row.addWidget(self._step_combo)

        speed_lbl = QtWidgets.QLabel("SPEED")
        speed_lbl.setObjectName("fieldLabel")
        self._speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._speed_slider.setMinimum(0)
        self._speed_slider.setMaximum(len(self.SPEED_CHOICES) - 1)
        self._speed_slider.setValue(1)
        self._speed_slider.setFixedWidth(120)
        self._speed_slider.valueChanged.connect(self._on_speed_changed)
        self._speed_value_lbl = QtWidgets.QLabel("Normal")
        self._speed_value_lbl.setObjectName("badge")
        lapse_row.addWidget(speed_lbl)
        lapse_row.addWidget(self._speed_slider)
        lapse_row.addWidget(self._speed_value_lbl)

        lapse_row.addStretch(1)
        outer.addLayout(lapse_row)

        # own row so a long message wraps instead of stretching the window
        self._status_label = QtWidgets.QLabel("")
        self._status_label.setObjectName("statusLabel")
        self._status_label.setWordWrap(True)
        outer.addWidget(self._status_label)

        # ---- figure card — now with almost the whole screen ----------------
        canvas_card = QtWidgets.QFrame()
        canvas_card.setObjectName("card")
        self._canvas_frame = QtWidgets.QVBoxLayout(canvas_card)
        self._canvas_frame.setContentsMargins(10, 10, 10, 10)
        outer.addWidget(canvas_card, stretch=1)

    # -- time-lapse -----------------------------------------------------------

    def _current_step(self) -> timedelta:
        return self.STEP_CHOICES[self._step_combo.currentIndex()][1]

    def _on_speed_changed(self, index: int) -> None:
        label, duration_ms = self.SPEED_CHOICES[index]
        self._speed_value_lbl.setText(label)
        if self._playing and self._step_start_local is not None:
            # Re-base the in-progress sweep on exactly where it is right
            # now, so changing speed mid-step doesn't snap the picture.
            elapsed_ms = self._step_elapsed.elapsed()
            old_duration_ms = max(self._step_duration_ms, 1)
            fraction = min(elapsed_ms / old_duration_ms, 1.0)
            self._step_start_local = self._step_start_local + self._current_step() * fraction
            self._step_elapsed.restart()
        self._step_duration_ms = duration_ms

    def _toggle_play(self) -> None:
        if not self._playing:
            # About to start: anchor the sweep on the current instant. Doing
            # this validation up front (instead of inside the frame tick)
            # means a bad input shows an error immediately rather than
            # flickering Play on and straight back off.
            try:
                moment, _ = self._read_inputs()
            except Exception as exc:
                self._status_label.setText(f"⚠ {exc}")
                return
            self._step_start_local = moment.local_dt
            self._step_duration_ms = self.SPEED_CHOICES[self._speed_slider.value()][1]
            self._step_elapsed.start()

        self._playing = not self._playing
        if self._playing:
            self._play_btn.setText("⏸")
            self._timer.start()
        else:
            self._play_btn.setText("▶")
            self._timer.stop()

    def _on_frame(self) -> None:
        if self._step_start_local is None:
            return

        elapsed_ms = self._step_elapsed.elapsed()
        duration_ms = max(self._step_duration_ms, 1)
        fraction = min(elapsed_ms / duration_ms, 1.0)

        # Interpolate between the step's start and end instants instead of
        # jumping straight to `start + step` -- this is what turns a
        # once-per-tick snap into a gradual sweep across every panel.
        interpolated_local = self._step_start_local + self._current_step() * fraction

        self._values["date"] = interpolated_local.strftime("%Y-%m-%d")
        self._values["time"] = interpolated_local.strftime("%H:%M:%S")
        self._refresh_summary_chip()
        self._show_moon()

        if fraction >= 1.0:
            self._step_start_local = interpolated_local
            self._step_elapsed.restart()

    def _go_home(self) -> None:
        if self._playing:
            self._toggle_play()
        self._quick_settings.hide()
        self.home_requested.emit()

    def _request_edit(self) -> None:
        if self._playing:
            self._toggle_play()
        self._quick_settings.hide()
        self.edit_requested.emit()

    def _toggle_quick_settings(self) -> None:
        if self._quick_settings.isVisible():
            self._quick_settings.hide()
            return
        # Always resync before showing, so quick settings reflects
        # whatever the simulation is actually showing right now (e.g.
        # after a time-lapse run, or after editing via the full wizard) -
        # not whatever it happened to hold the last time it was open.
        self._quick_settings.set_values(self._values)
        self._position_quick_settings()
        self._quick_settings.show()
        self._quick_settings.raise_()
        self._quick_settings.activateWindow()

    def _position_quick_settings(self) -> None:
        # Dock as a slim side panel flush against the right edge of the
        # app window, spanning nearly its full height - not a small
        # floating box that can run out of room for its own footer
        # buttons on a shorter screen. Recomputed every time the panel
        # opens, so it also tracks the window if it's been resized/moved.
        window = self.window()
        top_left = window.mapToGlobal(QtCore.QPoint(0, 0))
        margin = 12
        dialog = self._quick_settings
        panel_height = max(window.height() - margin * 2, 480)
        dialog.resize(dialog.PANEL_WIDTH, panel_height)
        x = top_left.x() + window.width() - dialog.width() - margin
        y = top_left.y() + margin
        dialog.move(max(x, 0), max(y, 0))

    def _on_quick_values_changed(self, values: dict) -> None:
        # Quick settings can change just one field at a time (date only,
        # time only, ...) - merge instead of replacing, so untouched
        # fields (like elevation) are left exactly as they were.
        if self._playing:
            self._toggle_play()
        self._values.update(values)
        self._refresh_summary_chip()
        self._show_moon()

    def apply_values(self, values: dict) -> None:
        self._values = dict(values)
        self._refresh_summary_chip()
        self._show_moon()

    # -- reading inputs / rendering --------------------------------------------

    def _refresh_summary_chip(self) -> None:
        v = self._values
        self._summary_chip.setText(
            f"{v.get('date', '')}  {v.get('time', '')}  {v.get('tz', '')}   ·   "
            f"{v.get('lat', '')}°, {v.get('lon', '')}°"
        )

    def _read_inputs(self) -> tuple[ObservationMoment, ObserverLocation]:
        raw = self._values

        try:
            year, month, day = (int(part) for part in raw["date"].split("-"))
        except ValueError:
            raise ValueError("Date must look like YYYY-MM-DD.")

        try:
            time_parts = [int(part) for part in raw["time"].split(":")]
            while len(time_parts) < 3:
                time_parts.append(0)
            hour, minute, second = time_parts
        except ValueError:
            raise ValueError("Time must look like HH:MM:SS.")

        try:
            local_dt = datetime(year, month, day, hour, minute, second)
        except ValueError as exc:
            raise ValueError(f"Invalid date/time: {exc}")

        try:
            lat = float(raw["lat"])
            lon = float(raw["lon"])
            elev = float(raw["elev"]) if raw.get("elev") else 0.0
        except ValueError:
            raise ValueError("Latitude, longitude and elevation must be numbers.")

        # Building the two immutable domain objects (see models/domain.py)
        # that MoonCalculator needs - this view never computes astronomy
        # itself, it only prepares the inputs for its MoonCalculator
        # collaborator.
        moment = ObservationMoment(local_dt=local_dt, timezone_name=raw["tz"])
        location = ObserverLocation(latitude_deg=lat, longitude_deg=lon, elevation_m=elev)
        return moment, location

    def _show_moon(self) -> None:
        try:
            moment, location = self._read_inputs()
            result = self._calculator.compute(moment, location)
        except Exception as exc:
            self._status_label.setText(f"⚠ {exc}")
            return

        self._status_label.setText("")
        self._render(result)

    def _render(self, result: MoonObservationResult) -> None:
        # Update the existing figure's artists in place. The canvas widget
        # itself is created only once (below) -- destroying and re-adding a
        # Qt widget every tick is what caused time-lapse playback to stutter.
        figure = self._figure_builder.update(result)

        if self._canvas is None:
            self._canvas = FigureCanvasQTAgg(figure)
            self._canvas_frame.addWidget(self._canvas)
        else:
            # draw_idle() schedules a repaint on the next event-loop pass
            # instead of blocking, which is what makes the sweep smooth.
            self._canvas.draw_idle()
