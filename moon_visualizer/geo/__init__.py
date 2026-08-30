"""
geo package
------------
Everything related to turning a raw (latitude, longitude) pair into
useful geographic context - timezone lookup, plus the bundled world
gazetteer used to search for a location by name - kept in its own small
package the same way `astronomy/` groups the Skyfield-facing code.
"""

from .timezone_resolver import TimezoneResolver
from .world_locations import ALL_LOCATIONS, FAVORITE_LOCATIONS, WorldLocation, find_by_name

__all__ = [
    "TimezoneResolver",
    "ALL_LOCATIONS",
    "FAVORITE_LOCATIONS",
    "WorldLocation",
    "find_by_name",
]
