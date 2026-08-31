"""
popups package
----------------
Floating dialogs that sit on top of a screen instead of replacing it.
Right now this is just QuickSettingsDialog, opened from MoonView.
"""

from .quick_settings_dialog import QuickSettingsDialog

__all__ = ["QuickSettingsDialog"]
