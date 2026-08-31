"""
panels/base_panel.py
---------------------
Defines the common contract that every 2D panel (Moon disk, sky dome,
calendar, clock, info text) must follow.
"""

from abc import ABC, abstractmethod

from ..models import MoonObservationResult


class Panel(ABC):
    """
    Common base class for every drawable panel in the figure.

    # OOP concept: ABSTRACTION (via an Abstract Base Class)
    # -------------------------------------------------------------------
    # `Panel` inherits from `ABC` and declares `draw()` as an
    # @abstractmethod: it describes WHAT every panel must be able to do
    # (draw itself onto a Matplotlib Axes, given a result) without saying
    # HOW. Python will refuse to create a subclass that forgets to
    # implement `draw()`, which documents and enforces the contract that
    # MoonFigureBuilder relies on.
    #
    # # OOP concept: INHERITANCE
    # -------------------------------------------------------------------
    # Every concrete panel (MoonDiskPanel, SkyPositionPanel, CalendarPanel,
    # AnalogClockPanel, InfoPanel) inherits from this class with
    # `class MoonDiskPanel(Panel):` and so on. They automatically share
    # this base's `_ax` bookkeeping and are guaranteed to expose `draw()`.
    #
    # # OOP concept: POLYMORPHISM
    # -------------------------------------------------------------------
    # MoonFigureBuilder.update() calls `panel.draw(ax, result)` on five
    # different objects without caring which concrete Panel subclass each
    # one is - each subclass's own `draw()` runs, drawing something
    # completely different (a disk, a sky dome, a calendar...). One call,
    # many different behaviours - that's polymorphism.
    """

    def __init__(self) -> None:
        # Shared, PROTECTED state (the leading underscore is Python's
        # convention for "internal to this class and its subclasses") -
        # every panel needs to remember which Axes it last drew on, so
        # subclasses inherit this bookkeeping instead of repeating it.
        self._ax = None

    @abstractmethod
    def draw(self, ax, result: MoonObservationResult) -> None:
        """Draw (or update) this panel's content on `ax` for `result`."""
        raise NotImplementedError
