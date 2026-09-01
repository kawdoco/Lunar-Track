"""
panels/sky_position_panel.py
------------------------------
Draws the polar "sky dome" showing the Moon's altitude/azimuth.
"""

import numpy as np

from ..theme import Theme
from ..models import MoonObservationResult
from .base_panel import Panel


class SkyPositionPanel(Panel):
    """Draws a polar 'sky dome' plot: the CENTER is the zenith and the
    OUTER RIM is the horizon. The angle around the circle is azimuth,
    measured clockwise from North, like a compass.

    # OOP concept: INHERITANCE / POLYMORPHISM
    # -------------------------------------------------------------------
    # Another Panel subclass with its own `draw()` override - see the
    # note in base_panel.py for the shared explanation.
    """

    def __init__(self) -> None:
        super().__init__()
        self._point_artist = None
        self._annotation = None

    def draw(self, ax, result: MoonObservationResult) -> None:
        if self._ax is not ax:
            self._build_static(ax)
            self._ax = ax

        theta = np.radians(result.azimuth_deg)

        if self._point_artist is not None:
            self._point_artist.remove()
            self._point_artist = None
        if self._annotation is not None:
            self._annotation.remove()
            self._annotation = None

        if result.altitude_deg >= 0:
            r = 90 - result.altitude_deg
            self._point_artist, = ax.plot(theta, r, "o", color=Theme.ACCENT, markersize=16,
                                           markeredgecolor=Theme.ACCENT_DIM, zorder=5)
            self._annotation = ax.annotate("Moon", (theta, r), textcoords="offset points",
                                            xytext=(10, 10), fontsize=9, color=Theme.TEXT)
        else:
            self._point_artist, = ax.plot(theta, 90, "x", color=Theme.TEXT_DIM, markersize=12,
                                           markeredgewidth=3, zorder=5)

        visible = "above" if result.altitude_deg >= 0 else "below"
        ax.set_title(f"Sky position ({visible} horizon)", fontsize=12, pad=15,
                     color=Theme.TEXT, fontweight="bold")

    def _build_static(self, ax) -> None:
        ax.clear()
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_ylim(0, 90)
        ax.set_yticks([0, 30, 60, 90])
        ax.set_yticklabels(["90°\n(zenith)", "60°", "30°", "0°\n(horizon)"],
                            fontsize=7, color=Theme.TEXT_DIM)
        ax.set_xticks(np.radians([0, 90, 180, 270]))
        ax.set_xticklabels(["N", "E", "S", "W"], fontsize=10, fontweight="bold",
                            color=Theme.TEXT)
        ax.grid(alpha=0.25, color=Theme.TEXT_DIM)
