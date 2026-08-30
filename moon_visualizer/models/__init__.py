"""
models package
---------------
Re-exports the domain classes so other packages can simply write
`from moon_visualizer.models import ObserverLocation` instead of reaching
into the `domain` submodule directly.
"""

from .domain import (
    ObserverLocation,
    ObservationMoment,
    MoonObservationResult,
    DEFAULT_OBSERVATION_VALUES,
)

__all__ = [
    "ObserverLocation",
    "ObservationMoment",
    "MoonObservationResult",
    "DEFAULT_OBSERVATION_VALUES",
]
