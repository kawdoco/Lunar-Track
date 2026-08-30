"""
astronomy/ephemeris_provider.py
--------------------------------
Loads the (large, slow-to-load) Skyfield timescale and JPL ephemeris file
exactly once per process, then hands the cached objects to anyone who asks.
"""

from skyfield.api import load


class EphemerisProvider:
    """
    Loads and caches the Skyfield timescale + JPL ephemeris once per
    process.

    # OOP concept: CLASS ATTRIBUTES AS SHARED STATE (Singleton-like cache)
    # -------------------------------------------------------------------
    # `_timescale` and `_ephemeris` are CLASS attributes (declared on the
    # class, not inside `__init__`), so all callers share exactly one
    # copy - there is no per-instance state at all, and in fact no
    # instance of this class is ever created. Combined with @classmethod,
    # this gives "load once, reuse everywhere" behaviour similar to the
    # classic Singleton design pattern, without the overhead of managing
    # an actual object.
    """

    _timescale = None
    _ephemeris = None

    @classmethod
    def timescale(cls):
        if cls._timescale is None:
            cls._timescale = load.timescale()
        return cls._timescale

    @classmethod
    def ephemeris(cls):
        if cls._ephemeris is None:
            cls._ephemeris = load("de421.bsp")
        return cls._ephemeris
