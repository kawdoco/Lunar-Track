"""
panels/calendar_panel.py
--------------------------
Draws a wall-calendar-style month grid with the current day circled.
"""

import calendar
from datetime import datetime

import matplotlib.patches as mpatches

from ..theme import Theme
from ..models import MoonObservationResult
from .base_panel import Panel


class CalendarPanel(Panel):
    """Draws a real month-grid calendar (like a wall calendar page) with the
    current observation day circled. The month grid is only rebuilt when the
    month/year actually changes -- a normal tick just slides the highlight
    circle from one day cell to the next, which is what keeps this smooth
    during time-lapse playback.

    # OOP concept: INHERITANCE / POLYMORPHISM
    # -------------------------------------------------------------------
    # Same pattern as the other panels: a Panel subclass with its own
    # private (`_`-prefixed) state and its own `draw()` implementation.
    """

    _WEEKDAY_LABELS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    _ROW_TOP = 5.25
    _ROW_HEIGHT = 0.86

    def __init__(self) -> None:
        super().__init__()
        self._year_month = None
        self._day_texts: dict[int, object] = {}
        self._day_positions: dict[int, tuple[float, float]] = {}
        self._highlight_circle = None
        self._highlighted_day = None
        self._month_title = None
        self._weekday_label = None

    def draw(self, ax, result: MoonObservationResult) -> None:
        local_dt = result.moment.aware_local
        year, month, today = local_dt.year, local_dt.month, local_dt.day

        if self._ax is not ax or self._year_month != (year, month):
            self._build_month(ax, year, month)
            self._ax = ax
            self._year_month = (year, month)

        if self._highlighted_day != today:
            if self._highlighted_day in self._day_texts:
                prev = self._day_texts[self._highlighted_day]
                prev.set_color(Theme.TEXT)
                prev.set_fontweight("normal")

            if self._highlight_circle is None:
                self._highlight_circle = mpatches.Circle(
                    self._day_positions[today], 0.36, facecolor=Theme.ACCENT,
                    edgecolor=Theme.ACCENT_DIM, linewidth=1.4, zorder=2,
                )
                ax.add_patch(self._highlight_circle)
            else:
                self._highlight_circle.center = self._day_positions[today]

            current = self._day_texts[today]
            current.set_color("#16171f")
            current.set_fontweight("bold")
            self._highlighted_day = today

        self._weekday_label.set_text(local_dt.strftime("%A"))
        ax.set_title("Date", fontsize=12, pad=10, color=Theme.TEXT, fontweight="bold")

    def _build_month(self, ax, year: int, month: int) -> None:
        ax.clear()
        ax.axis("off")
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 7.4)
        ax.set_aspect("equal")

        self._day_texts = {}
        self._day_positions = {}
        self._highlight_circle = None
        self._highlighted_day = None

        month_name = datetime(year, month, 1).strftime("%B %Y")
        self._month_title = ax.text(3.5, 7.05, month_name, ha="center", va="center",
                                     fontsize=13, fontweight="bold", color=Theme.ACCENT)

        for i, wd in enumerate(self._WEEKDAY_LABELS):
            ax.text(i + 0.5, 6.15, wd, ha="center", va="center",
                    fontsize=9, fontweight="bold", color=Theme.TEXT_DIM)
        ax.plot([0.1, 6.9], [5.78, 5.78], color=Theme.BORDER, linewidth=1, zorder=1)

        weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
        for week_idx, week in enumerate(weeks):
            y = self._ROW_TOP - week_idx * self._ROW_HEIGHT
            for day_idx, day_num in enumerate(week):
                if day_num == 0:
                    continue
                x = day_idx + 0.5
                self._day_positions[day_num] = (x, y)
                self._day_texts[day_num] = ax.text(
                    x, y, str(day_num), ha="center", va="center",
                    fontsize=9.5, fontweight="normal", color=Theme.TEXT, zorder=3,
                )

        self._weekday_label = ax.text(
            3.5, self._ROW_TOP - len(weeks) * self._ROW_HEIGHT - 0.35, "",
            ha="center", va="center", fontsize=10, color=Theme.TEXT_DIM, style="italic",
        )
