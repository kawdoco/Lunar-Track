"""
panels/info_panel.py
----------------------
Draws the plain-text "Details" panel listing all computed values.
"""

from ..theme import Theme
from ..models import MoonObservationResult
from .base_panel import Panel


class InfoPanel(Panel):
    """Renders a plain-text information panel with all computed values.
    The text lines are created once and their strings are updated in
    place afterward rather than clearing and re-adding them every frame.

    # OOP concept: INHERITANCE / POLYMORPHISM
    # -------------------------------------------------------------------
    # The final Panel subclass - completes the family of interchangeable
    # panels that MoonFigureBuilder treats uniformly through the shared
    # `draw()` interface.
    """

    def __init__(self) -> None:
        super().__init__()
        self._text_artists: list = []

    def draw(self, ax, result: MoonObservationResult) -> None:
        location = result.location

        lines = [
            "Observer location",
            f"  Latitude   : {location.latitude_deg:.4f}°",
            f"  Longitude  : {location.longitude_deg:.4f}°",
            f"  Elevation  : {location.elevation_m:.0f} m",
            "",
            "Moon position (topocentric)",
            f"  Altitude   : {result.altitude_deg:.2f}°",
            f"  Azimuth    : {result.azimuth_deg:.2f}°",
            f"  Distance   : {result.distance_km:,.0f} km",
            "",
            "Moon phase",
            f"  Phase name   : {result.phase_name}",
            f"  Illumination : {result.illum_fraction * 100:.1f}%",
            f"  Phase angle  : {result.phase_angle_deg:.1f}°",
        ]

        if self._ax is not ax or len(self._text_artists) != len(lines):
            self._build_static(ax, lines)
            self._ax = ax
        else:
            for artist, text in zip(self._text_artists, lines):
                artist.set_text(text)

        ax.set_title("Details", fontsize=12, pad=10, color=Theme.TEXT, fontweight="bold")

    def _build_static(self, ax, lines: list[str]) -> None:
        ax.clear()
        ax.axis("off")
        self._text_artists = []

        y = 0.98
        for text in lines:
            is_header = bool(text) and not text.startswith(" ")
            artist = ax.text(0.02, y, text, transform=ax.transAxes,
                              fontsize=11 if is_header else 10,
                              fontweight="bold" if is_header else "normal",
                              color=Theme.ACCENT if is_header else Theme.TEXT,
                              va="top", family="monospace")
            self._text_artists.append(artist)
            y -= 0.052
