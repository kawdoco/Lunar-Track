"""
widgets package
----------------
Small, reusable Qt widgets that don't belong to any one screen.

WorldMapWidget is the low-level clickable map; LocationPickerWidget
composes it with a search box, coordinate/elevation fields and timezone
auto-detect into the ONE location-picking UI shared by both the Quick
Settings popup and the full setup wizard's location step.
"""

from .world_map_widget import WorldMapWidget
from .location_picker_widget import LocationPickerWidget
from .flow_layout import FlowLayout

__all__ = ["WorldMapWidget", "LocationPickerWidget", "FlowLayout"]
