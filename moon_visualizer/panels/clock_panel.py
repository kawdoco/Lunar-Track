"""
panels/clock_panel.py
-----------------------
Draws an analog clock face with a digital readout underneath.
"""

import numpy as np
import matplotlib.patches as mpatches

from ..theme import Theme
from ..models import MoonObservationResult
from .base_panel import Panel


class AnalogClockPanel(Panel):
    """Draws an analog clock face (hour/minute/second hands) with a small
    digital readout underneath. The face and the 60 tick marks are drawn
    once; every later frame just moves the three hand lines and updates the
    digital text, so the second hand can sweep smoothly during time-lapse.

    # OOP concept: INHERITANCE / POLYMORPHISM
    # -------------------------------------------------------------------
    # Same Panel-subclass pattern again - each panel type encapsulates its
    # own drawing state and knows how to update only itself.
    """

    def __init__(self) -> None:
        super().__init__()
        self._hour_hand = None
        self._minute_hand = None
        self._second_hand = None
        self._digital_text = None
        self._tz_text = None

    def draw(self, ax, result: MoonObservationResult) -> None:
        if self._ax is not ax:
            self._build_face(ax)
            self._ax = ax

        local_dt = result.moment.aware_local
        hour, minute, second = local_dt.hour % 12, local_dt.minute, local_dt.second

        hour_angle = np.radians(90 - (hour + minute / 60) * 30)
        minute_angle = np.radians(90 - (minute + second / 60) * 6)
        second_angle = np.radians(90 - second * 6)

        self._hour_hand.set_data([0, 0.48 * np.cos(hour_angle)], [0, 0.48 * np.sin(hour_angle)])
        self._minute_hand.set_data([0, 0.72 * np.cos(minute_angle)], [0, 0.72 * np.sin(minute_angle)])
        self._second_hand.set_data([0, 0.8 * np.cos(second_angle)], [0, 0.8 * np.sin(second_angle)])

        tz_label = local_dt.strftime("%Z") or result.moment.timezone_name
        self._digital_text.set_text(local_dt.strftime("%H:%M:%S"))
        self._tz_text.set_text(tz_label)

        ax.set_title("Time", fontsize=12, pad=10, color=Theme.TEXT, fontweight="bold")

    def _build_face(self, ax) -> None:
        ax.clear()
        ax.axis("off")
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.55, 1.25)
        ax.set_aspect("equal")

        ax.add_patch(mpatches.Circle((0, 0), 1.0, facecolor=Theme.BG_PANEL_2,
                                      edgecolor=Theme.ACCENT_DIM, linewidth=1.4, zorder=1))

        for i in range(60):
            angle = np.radians(90 - i * 6)
            is_hour = i % 5 == 0
            r_in = 0.82 if is_hour else 0.88
            x_in, y_in = r_in * np.cos(angle), r_in * np.sin(angle)
            x_out, y_out = 0.94 * np.cos(angle), 0.94 * np.sin(angle)
            ax.plot([x_in, x_out], [y_in, y_out], color=Theme.TEXT_DIM,
                    linewidth=1.8 if is_hour else 0.7, zorder=2)

        self._hour_hand, = ax.plot([], [], color=Theme.TEXT, linewidth=3.6,
                                    solid_capstyle="round", zorder=4)
        self._minute_hand, = ax.plot([], [], color=Theme.TEXT, linewidth=2.4,
                                      solid_capstyle="round", zorder=4)
        self._second_hand, = ax.plot([], [], color=Theme.DANGER, linewidth=1,
                                      solid_capstyle="round", zorder=5)
        ax.add_patch(mpatches.Circle((0, 0), 0.05, facecolor=Theme.ACCENT,
                                      edgecolor=Theme.ACCENT_DIM, zorder=6))

        self._digital_text = ax.text(0, -1.24, "", ha="center", va="center",
                                      fontsize=13, fontweight="bold", color=Theme.TEXT,
                                      family="monospace")
        self._tz_text = ax.text(0, -1.44, "", ha="center", va="center",
                                 fontsize=8.5, color=Theme.TEXT_DIM)
