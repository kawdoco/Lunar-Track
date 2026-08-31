"""
panels/figure_builder.py
--------------------------
Assembles the whole Matplotlib figure out of the individual Panel objects.
"""

import matplotlib.pyplot as plt

from ..theme import Theme
from ..models import MoonObservationResult
from .moon_disk_panel import MoonDiskPanel
from .sky_position_panel import SkyPositionPanel
from .calendar_panel import CalendarPanel
from .clock_panel import AnalogClockPanel
from .info_panel import InfoPanel


class MoonFigureBuilder:
    """Assembles the 5-panel figure (Moon disk | sky position | date+time |
    info panel) from a MoonObservationResult.

    The Figure and its Axes are created ONCE, on the first call to
    get_figure()/update(). Every subsequent update() call re-uses the same
    Axes and hands the result to each panel, which mutates its own cached
    artists rather than rebuilding from scratch -- so time-lapse playback
    just updates numbers/positions instead of re-laying out a brand new
    figure ~10+ times a second.

    # OOP concept: COMPOSITION ("has-a" relationships)
    # -------------------------------------------------------------------
    # MoonFigureBuilder does not inherit from any of the five Panel
    # classes - it HOLDS one instance of each as attributes, built once in
    # `__init__`. This lets it treat the whole set as interchangeable
    # collaborators: `update()` just loops through them and calls the
    # shared `draw()` interface on each (see the POLYMORPHISM note in
    # base_panel.py), without knowing or caring what each one draws.
    """

    def __init__(self) -> None:
        self._disk_panel = MoonDiskPanel()
        self._sky_panel = SkyPositionPanel()
        self._calendar_panel = CalendarPanel()
        self._clock_panel = AnalogClockPanel()
        self._info_panel = InfoPanel()
        self._fig = None
        self._axes = None
        self._suptitle = None

    def get_figure(self, figsize=(15.8, 6.6)):
        if self._fig is None:
            fig = plt.Figure(figsize=figsize)
            fig.patch.set_facecolor(Theme.BG_PANEL)
            gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 0.85, 1.05], wspace=0.4)

            ax_moon = fig.add_subplot(gs[0, 0])
            ax_sky = fig.add_subplot(gs[0, 1], projection="polar")
            gs_datetime = gs[0, 2].subgridspec(2, 1, height_ratios=[1.2, 1], hspace=0.4)
            ax_calendar = fig.add_subplot(gs_datetime[0, 0])
            ax_clock = fig.add_subplot(gs_datetime[1, 0])
            ax_info = fig.add_subplot(gs[0, 3])

            for ax in (ax_moon, ax_sky, ax_calendar, ax_clock, ax_info):
                ax.set_facecolor(Theme.BG_PANEL)

            self._axes = dict(moon=ax_moon, sky=ax_sky, calendar=ax_calendar,
                               clock=ax_clock, info=ax_info)
            self._suptitle = fig.suptitle("", fontsize=13, fontweight="bold", color=Theme.TEXT)
            fig.tight_layout(rect=[0, 0, 1, 0.93])
            self._fig = fig
        return self._fig

    def update(self, result: MoonObservationResult):
        fig = self.get_figure()

        # Polymorphism in action: five different concrete Panel subclasses,
        # called uniformly through the exact same `draw(ax, result)` shape.
        self._disk_panel.draw(self._axes["moon"], result)
        self._sky_panel.draw(self._axes["sky"], result)
        self._calendar_panel.draw(self._axes["calendar"], result)
        self._clock_panel.draw(self._axes["clock"], result)
        self._info_panel.draw(self._axes["info"], result)

        self._suptitle.set_text(
            f"Moon appearance — {result.moment.aware_local.strftime('%Y-%m-%d %H:%M %Z')} "
            f"at ({result.location.latitude_deg:.3f}°, {result.location.longitude_deg:.3f}°)"
        )
        return fig
