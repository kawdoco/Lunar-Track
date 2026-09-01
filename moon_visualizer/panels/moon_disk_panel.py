"""
panels/moon_disk_panel.py
--------------------------
Draws the realistic waxing/waning Moon disk.
"""

import numpy as np
import matplotlib.patches as mpatches

from ..theme import Theme
from ..models import MoonObservationResult
from .base_panel import Panel


class MoonDiskPanel(Panel):
    """
    Draws a realistic Moon-phase disk on a given Axes.

    Geometry: the terminator (day/night boundary) is always a half-ellipse.
    For a phase angle `pa` (0=new, 180=full), the terminator's horizontal
    position on a unit-radius disk is:

        x_t(y) = cos(pa) * sqrt(1 - y^2)

    Waxing (0 < pa < 180): light grows outward from the right limb.
    Waning (180 < pa < 360): light shrinks back toward the left limb.

    # OOP concept: INHERITANCE + METHOD OVERRIDING
    # -------------------------------------------------------------------
    # `class MoonDiskPanel(Panel)` inherits the `_ax` bookkeeping and the
    # `draw()` contract from Panel, then OVERRIDES `draw()` with its own
    # concrete implementation - satisfying the abstract method the base
    # class demanded.
    """

    _RADIUS = 1.0

    def __init__(self) -> None:
        super().__init__()  # let the base class set up shared state (self._ax)
        self._fill_artist = None

    def draw(self, ax, result: MoonObservationResult) -> None:
        if self._ax is not ax:
            self._build_static(ax)
            self._ax = ax

        if self._fill_artist is not None:
            self._fill_artist.remove()
            self._fill_artist = None

        y = np.linspace(-self._RADIUS, self._RADIUS, 200)
        half_width = np.sqrt(np.clip(self._RADIUS ** 2 - y ** 2, 0, None))
        pa_rad = np.radians(result.phase_angle_deg)
        x_term = np.cos(pa_rad) * half_width
        waxing = result.phase_angle_deg < 180

        if waxing:
            self._fill_artist = ax.fill_betweenx(y, x_term, half_width, color=Theme.MOON_LIT, zorder=2)
        else:
            self._fill_artist = ax.fill_betweenx(y, -half_width, -x_term, color=Theme.MOON_LIT, zorder=2)

        ax.set_title(f"Illumination: {result.illum_fraction * 100:.1f}%",
                     fontsize=12, pad=10, color=Theme.TEXT, fontweight="bold")

    def _build_static(self, ax) -> None:
        # A leading single underscore marks this as an internal ("private")
        # helper - part of this class's encapsulated implementation detail,
        # not something outside code is meant to call directly.
        ax.clear()
        ax.add_patch(mpatches.Circle(
            (0, 0), self._RADIUS, facecolor=Theme.MOON_DARK,
            edgecolor="#6c7291", linewidth=1.2, zorder=1,
        ))
        ax.add_patch(mpatches.Circle(
            (0, 0), self._RADIUS, facecolor="none",
            edgecolor="#6c7291", linewidth=1.2, zorder=3,
        ))
        ax.set_xlim(-1.25, 1.25)
        ax.set_ylim(-1.25, 1.25)
        ax.set_aspect("equal")
        ax.axis("off")
