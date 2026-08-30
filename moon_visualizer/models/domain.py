"""
models/domain.py
-----------------
The "nouns" of the app: plain data-holding classes that describe a place on
Earth, a moment in time, and the result of observing the Moon from that
place at that moment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class ObserverLocation:
    """
    A point on Earth's surface where the Moon is being observed from.

    # OOP concept: ENCAPSULATION + IMMUTABILITY
    # -------------------------------------------------------------------
    # `latitude_deg`, `longitude_deg` and `elevation_m` are bundled inside
    # one object instead of being passed around the program as three loose
    # numbers. `@dataclass(frozen=True)` also makes every instance
    # IMMUTABLE - once created it can never be changed - which is a
    # stronger form of encapsulation: nothing elsewhere in the code can
    # accidentally corrupt a location after it was built.
    """

    latitude_deg: float          # positive = North, negative = South
    longitude_deg: float         # positive = East,  negative = West
    elevation_m: float = 0.0     # meters above sea level (small effect on Alt/Az)

    def validate(self) -> None:
        """
        A METHOD (a function that belongs to this class and operates on
        its own data via `self`) that enforces the object's own rules.
        Keeping validation here, next to the data it checks, is another
        expression of encapsulation.
        """
        if not -90.0 <= self.latitude_deg <= 90.0:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        if not -180.0 <= self.longitude_deg <= 180.0:
            raise ValueError("Longitude must be between -180 and 180 degrees.")


@dataclass(frozen=True)
class ObservationMoment:
    """A local civil date/time, tied to an IANA timezone name."""

    local_dt: datetime           # naive local datetime
    timezone_name: str           # e.g. "Asia/Colombo", "UTC"

    def validate(self) -> None:
        ZoneInfo(self.timezone_name)

    @property
    def aware_local(self) -> datetime:
        """
        # OOP concept: PROPERTY (computed attribute)
        # ---------------------------------------------------------------
        # `@property` lets callers write `moment.aware_local` as if it
        # were a plain stored field, while it is really being calculated
        # fresh every time from `local_dt` + `timezone_name`. This hides
        # the calculation behind a simple attribute-style interface -
        # another form of encapsulation.
        """
        return self.local_dt.replace(tzinfo=ZoneInfo(self.timezone_name))

    @property
    def utc(self) -> datetime:
        return self.aware_local.astimezone(ZoneInfo("UTC"))


@dataclass(frozen=True)
class MoonObservationResult:
    """
    Everything derived for one (moment, location) pair - ready to display.

    # OOP concept: COMPOSITION
    # -------------------------------------------------------------------
    # This class doesn't inherit from ObserverLocation / ObservationMoment;
    # instead it HOLDS one of each as fields. That "object A contains
    # object B" relationship is composition, and it models the real-world
    # idea that "a result is built FROM a moment and a location" more
    # naturally than inheritance would.
    """

    moment: ObservationMoment
    location: ObserverLocation
    altitude_deg: float
    azimuth_deg: float
    distance_km: float
    illum_fraction: float
    phase_angle_deg: float
    phase_name: str


# Default values shown the first time the wizard opens (and used by the
# Home page's "jump in with defaults" shortcut). Plain module-level data,
# not tied to any one class, so it stays outside the OOP structure above.
DEFAULT_OBSERVATION_VALUES = {
    "date": "2026-08-26",
    "time": "20:30:00",
    "tz": "Asia/Colombo",
    "lat": "6.6828",
    "lon": "80.4012",
    "elev": "90",
}
