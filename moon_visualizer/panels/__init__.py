"""
panels package
---------------
Everything that draws onto a Matplotlib Axes: the abstract Panel base
class, the five concrete panels, and the MoonFigureBuilder that composes
them into one figure.
"""

from .base_panel import Panel
from .moon_disk_panel import MoonDiskPanel
from .sky_position_panel import SkyPositionPanel
from .calendar_panel import CalendarPanel
from .clock_panel import AnalogClockPanel
from .info_panel import InfoPanel
from .figure_builder import MoonFigureBuilder

__all__ = [
    "Panel",
    "MoonDiskPanel",
    "SkyPositionPanel",
    "CalendarPanel",
    "AnalogClockPanel",
    "InfoPanel",
    "MoonFigureBuilder",
]
