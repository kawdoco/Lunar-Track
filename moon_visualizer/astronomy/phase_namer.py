"""
astronomy/phase_namer.py
-------------------------
Turns a raw phase-angle number into a human-friendly name like "Full Moon".
"""


class MoonPhaseNamer:
    """
    Maps a 0-360 degree phase angle to one of the 8 traditional Moon phase
    names.

    # OOP concept: CLASS METHOD + "STATELESS SERVICE" CLASS
    # -------------------------------------------------------------------
    # This class never needs an instance (`MoonPhaseNamer()`) - it is used
    # purely as a namespace for one @classmethod. Grouping the boundary
    # table and the lookup logic in a class (instead of a bare function)
    # keeps the data (`_BOUNDARIES`) and the behaviour that interprets it
    # (`name_for`) tied together, which is the essence of OOP even without
    # any per-instance state.
    """

    _BOUNDARIES = [
        (22.5, "New Moon"),
        (67.5, "Waxing Crescent"),
        (112.5, "First Quarter"),
        (157.5, "Waxing Gibbous"),
        (202.5, "Full Moon"),
        (247.5, "Waning Gibbous"),
        (292.5, "Last Quarter"),
        (337.5, "Waning Crescent"),
        (360.1, "New Moon"),
    ]

    @classmethod
    def name_for(cls, phase_angle_deg: float) -> str:
        # `cls` (the class itself) is passed automatically instead of
        # `self` (an instance) - a classmethod, so it can be called as
        # `MoonPhaseNamer.name_for(...)` without ever building an object.
        pa = phase_angle_deg % 360
        for limit, name in cls._BOUNDARIES:
            if pa < limit:
                return name
        return "New Moon"
