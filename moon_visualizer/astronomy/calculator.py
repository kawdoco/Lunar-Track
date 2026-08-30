"""
astronomy/calculator.py
------------------------
The single place in the app that talks to Skyfield and turns
(moment, location) into a fully-computed MoonObservationResult.
"""

from skyfield.api import wgs84
from skyfield import almanac

from ..models import ObservationMoment, ObserverLocation, MoonObservationResult
from .ephemeris_provider import EphemerisProvider
from .phase_namer import MoonPhaseNamer


class MoonCalculator:
    """
    Computes the Moon's Alt/Az position and illumination/phase data for a
    given observation moment and observer location.

    # OOP concept: COMPOSITION + SINGLE RESPONSIBILITY
    # -------------------------------------------------------------------
    # MoonCalculator does not inherit from EphemerisProvider or
    # MoonPhaseNamer - it simply USES them (composition: "has-a"
    # relationship via collaborating classes) to do its one job: turn raw
    # inputs into a MoonObservationResult. Each of the three classes has a
    # single, narrow responsibility (loading data / naming a phase /
    # running the calculation), which makes each one easy to test and
    # reuse on its own.
    """

    def compute(
        self, moment: ObservationMoment, location: ObserverLocation
    ) -> MoonObservationResult:
        moment.validate()
        location.validate()

        ts = EphemerisProvider.timescale()
        eph = EphemerisProvider.ephemeris()
        earth, moon = eph["earth"], eph["moon"]

        utc_dt = moment.utc
        t = ts.utc(
            utc_dt.year, utc_dt.month, utc_dt.day,
            utc_dt.hour, utc_dt.minute, utc_dt.second,
        )

        observer = earth + wgs84.latlon(
            location.latitude_deg, location.longitude_deg,
            elevation_m=location.elevation_m,
        )

        apparent_moon = observer.at(t).observe(moon).apparent()
        alt, az, distance = apparent_moon.altaz()

        illum_fraction = almanac.fraction_illuminated(eph, "moon", t)
        phase_angle = almanac.moon_phase(eph, t).degrees % 360

        return MoonObservationResult(
            moment=moment,
            location=location,
            altitude_deg=alt.degrees,
            azimuth_deg=az.degrees,
            distance_km=distance.km,
            illum_fraction=illum_fraction,
            phase_angle_deg=phase_angle,
            phase_name=MoonPhaseNamer.name_for(phase_angle),
        )
