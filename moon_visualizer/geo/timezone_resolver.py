"""
geo/timezone_resolver.py
--------------------------
TimezoneResolver - turns a (latitude, longitude) pair picked on the map
into an IANA timezone name ("Asia/Colombo", "Europe/London", ...) so the
Quick Settings popup can keep the timezone field in sync with the map
automatically, without the user having to look it up themselves.
"""

from __future__ import annotations

from zoneinfo import ZoneInfo


class TimezoneResolver:
    """
    Resolves the IANA timezone name for a point on Earth.

    # OOP concept: ABSTRACTION + ENCAPSULATION
    # -----------------------------------------------------------------
    # Callers just ask `resolve(lat, lon)` and get back a timezone name
    # string - they never need to know whether that answer came from the
    # precise `timezonefinder` package or from the coarse longitude-only
    # fallback below. Which strategy is available is decided once, in
    # `__init__`, and hidden behind this one method - the "how" is fully
    # encapsulated inside this class.
    #
    # This also mirrors `EphemerisProvider` in astronomy/: a class-level
    # resource (here, the on-disk timezone-boundary data) is loaded once
    # and reused, instead of every call paying the load cost again.
    """

    def __init__(self) -> None:
        self._finder = None
        try:
            # timezonefinder is an *optional* dependency - the app should
            # still run without it, just with a less precise fallback.
            from timezonefinder import TimezoneFinder

            self._finder = TimezoneFinder()
        except Exception:
            self._finder = None

    @property
    def is_precise(self) -> bool:
        """True when real timezone-boundary data (timezonefinder) is available."""
        return self._finder is not None

    def resolve(self, latitude_deg: float, longitude_deg: float) -> str | None:
        """
        Returns the best-guess IANA timezone name for this point, or None
        if nothing at all could be determined (invalid coordinates).
        """
        if self._finder is not None:
            try:
                tz_name = self._finder.timezone_at(lng=longitude_deg, lat=latitude_deg)
                if tz_name is None:
                    # Happens right on/near a border or over open ocean -
                    # widen the search instead of giving up.
                    tz_name = self._finder.closest_timezone_at(lng=longitude_deg, lat=latitude_deg)
                if tz_name and self._is_valid(tz_name):
                    return tz_name
            except Exception:
                pass  # fall through to the approximate fallback below

        return self._approximate(longitude_deg)

    @staticmethod
    def _is_valid(tz_name: str) -> bool:
        try:
            ZoneInfo(tz_name)
            return True
        except Exception:
            return False

    @staticmethod
    def _approximate(longitude_deg: float) -> str:
        """
        Coarse fallback used only when `timezonefinder` isn't installed:
        one fixed zone per 15 degrees of longitude, no daylight-saving
        and no respect for actual country borders. Good enough to avoid
        leaving the timezone field wrong-hemisphere-wrong, not meant to
        be exact.
        """
        offset_hours = round(longitude_deg / 15.0)
        offset_hours = max(-12, min(14, offset_hours))
        if offset_hours == 0:
            return "UTC"
        # "Etc/GMT" zone names use the OPPOSITE sign convention to normal
        # UTC offsets (POSIX historical quirk): Etc/GMT-5 is UTC+5.
        sign = "-" if offset_hours > 0 else "+"
        return f"Etc/GMT{sign}{abs(offset_hours)}"
