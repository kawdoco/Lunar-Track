"""
theme.py
--------
Central place for colours and the global Qt stylesheet, so every widget in
the app (and the embedded Matplotlib figure) uses the same palette.
"""

from PySide6 import QtWidgets


class Theme:
    """
    Groups every colour constant the app uses under a single namespace.

    # OOP concept: ENCAPSULATION
    # -----------------------------------------------------------------
    # Instead of scattering colour hex-codes across dozens of files, they
    # are all bundled ("encapsulated") inside this one class. Every other
    # module reaches the same values through `Theme.BG`, `Theme.ACCENT`,
    # etc. If the palette ever changes, only this class needs editing.
    #
    # Note there are no instances of Theme anywhere in the app - it is
    # used purely as a namespace of CLASS ATTRIBUTES (shared, constant
    # data that belongs to the class itself, not to any particular
    # object built from it).
    """

    BG            = "#12141c"   # app background
    BG_PANEL      = "#1b1e2b"   # cards / group boxes
    BG_PANEL_2    = "#232738"   # inputs / nested surfaces
    BORDER        = "#323852"
    TEXT          = "#eceef5"
    TEXT_DIM      = "#9095ab"
    ACCENT        = "#f4c542"   # moonlight gold
    ACCENT_DIM    = "#c79f2e"
    ACCENT_SOFT   = "#40405a"
    MOON_LIT      = "#f4f1d9"
    MOON_DARK     = "#262838"
    DANGER        = "#ff6b81"


# The stylesheet itself is just a formatted string built from Theme's
# attributes - it is not part of the OOP design, so it stays as plain
# module-level data.
STYLE_SHEET = f"""
QWidget {{
    background-color: {Theme.BG};
    color: {Theme.TEXT};
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {Theme.BG};
}}

QFrame#card, QGroupBox {{
    background-color: {Theme.BG_PANEL};
    border: 1px solid {Theme.BORDER};
    border-radius: 12px;
}}

QGroupBox {{
    margin-top: 14px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {Theme.ACCENT};
}}

QLabel {{
    background: transparent;
}}
QLabel#h1 {{
    font-size: 26px;
    font-weight: 700;
    color: {Theme.TEXT};
}}
QLabel#h2 {{
    font-size: 15px;
    color: {Theme.TEXT_DIM};
}}
QLabel#stepHeading {{
    font-size: 20px;
    font-weight: 700;
    color: {Theme.TEXT};
}}
QLabel#sectionTitle {{
    font-size: 13px;
    font-weight: 700;
    color: {Theme.ACCENT};
}}
QLabel#fieldLabel {{
    color: {Theme.TEXT_DIM};
    font-size: 11px;
}}
QLabel#statusLabel {{
    color: {Theme.DANGER};
    font-weight: 600;
}}
QLabel#badge {{
    background-color: {Theme.BG_PANEL_2};
    border: 1px solid {Theme.BORDER};
    border-radius: 8px;
    padding: 8px 10px;
    color: {Theme.TEXT_DIM};
}}
QLabel#summaryChip {{
    background-color: {Theme.BG_PANEL_2};
    border: 1px solid {Theme.BORDER};
    border-radius: 10px;
    padding: 7px 14px;
    font-size: 12px;
    color: {Theme.TEXT_DIM};
}}
QLabel#reviewValue {{
    font-size: 15px;
    font-weight: 600;
    color: {Theme.TEXT};
}}

QLineEdit, QComboBox, QDateEdit, QTimeEdit, QDoubleSpinBox, QSpinBox {{
    background-color: {Theme.BG_PANEL_2};
    border: 1px solid {Theme.BORDER};
    border-radius: 7px;
    padding: 6px 8px;
    color: {Theme.TEXT};
    selection-background-color: {Theme.ACCENT_DIM};
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus,
QDoubleSpinBox:focus, QSpinBox:focus {{
    border: 1px solid {Theme.ACCENT};
}}
QDateEdit::drop-down, QTimeEdit::drop-down {{
    border: none;
    width: 20px;
}}
QDateEdit QCalendarWidget {{
    background-color: {Theme.BG_PANEL};
}}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QSpinBox::up-button, QSpinBox::down-button {{
    width: 16px;
    background-color: {Theme.BG_PANEL_2};
    border-left: 1px solid {Theme.BORDER};
}}
QCheckBox {{
    color: {Theme.TEXT};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {Theme.BORDER};
    border-radius: 4px;
    background-color: {Theme.BG_PANEL_2};
}}
QCheckBox::indicator:checked {{
    background-color: {Theme.ACCENT};
    border: 1px solid {Theme.ACCENT};
}}
QLineEdit[fieldState="error"] {{
    border: 1px solid {Theme.DANGER};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {Theme.BG_PANEL_2};
    color: {Theme.TEXT};
    selection-background-color: {Theme.ACCENT_DIM};
    border: 1px solid {Theme.BORDER};
    outline: none;
}}

QPushButton {{
    background-color: {Theme.BG_PANEL_2};
    border: 1px solid {Theme.BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    color: {Theme.TEXT};
    font-weight: 600;
}}
QPushButton:hover {{
    border: 1px solid {Theme.ACCENT};
    color: {Theme.ACCENT};
}}
QPushButton:pressed {{
    background-color: {Theme.ACCENT_SOFT};
}}
QPushButton#primary {{
    background-color: {Theme.ACCENT};
    border: 1px solid {Theme.ACCENT};
    color: #16171f;
    font-size: 14px;
    padding: 12px 26px;
}}
QPushButton#primary:hover {{
    background-color: {Theme.ACCENT_DIM};
    border: 1px solid {Theme.ACCENT_DIM};
    color: #16171f;
}}
QPushButton#secondary {{
    background-color: transparent;
    border: 1px solid {Theme.BORDER};
    color: {Theme.TEXT};
}}
QPushButton#secondary:hover {{
    border: 1px solid {Theme.ACCENT};
    color: {Theme.ACCENT};
}}
QPushButton#ghost {{
    background-color: transparent;
    border: 1px solid transparent;
    color: {Theme.TEXT_DIM};
}}
QPushButton#ghost:hover {{
    color: {Theme.ACCENT};
}}
QPushButton#chipButton {{
    background-color: {Theme.BG_PANEL_2};
    border: 1px solid {Theme.BORDER};
    border-radius: 14px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
    color: {Theme.TEXT_DIM};
}}
QPushButton#chipButton:hover {{
    border: 1px solid {Theme.ACCENT};
    color: {Theme.ACCENT};
}}
QPushButton#playButton {{
    background-color: {Theme.ACCENT};
    border: 1px solid {Theme.ACCENT};
    color: #16171f;
    font-size: 15px;
    min-width: 38px;
    min-height: 38px;
    border-radius: 19px;
    padding: 0px;
}}
QPushButton#playButton:hover {{
    background-color: {Theme.ACCENT_DIM};
}}

QSlider::groove:horizontal {{
    height: 6px;
    background: {Theme.BG_PANEL_2};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {Theme.ACCENT};
    width: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::sub-page:horizontal {{
    background: {Theme.ACCENT_DIM};
    border-radius: 3px;
}}

QLabel#stepDot {{
    background-color: {Theme.BG_PANEL_2};
    border: 1px solid {Theme.BORDER};
    border-radius: 15px;
    font-weight: 700;
    color: {Theme.TEXT_DIM};
}}
QLabel#stepDot[stepState="active"] {{
    background-color: {Theme.ACCENT};
    border: 1px solid {Theme.ACCENT};
    color: #16171f;
}}
QLabel#stepDot[stepState="done"] {{
    background-color: {Theme.ACCENT_SOFT};
    border: 1px solid {Theme.ACCENT_DIM};
    color: {Theme.ACCENT};
}}
QLabel#stepName {{
    color: {Theme.TEXT_DIM};
    font-size: 11px;
    font-weight: 600;
}}
QLabel#stepName[stepState="active"] {{
    color: {Theme.ACCENT};
}}
QFrame#stepConnector {{
    background-color: {Theme.BORDER};
}}

QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {Theme.BORDER};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {Theme.ACCENT_SOFT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QWidget#panelHeader {{
    background-color: {Theme.BG_PANEL};
    border-bottom: 1px solid {Theme.BORDER};
}}
QWidget#panelFooter {{
    background-color: {Theme.BG_PANEL};
    border-top: 1px solid {Theme.BORDER};
}}
"""


def mark_field_error(edit: QtWidgets.QLineEdit, is_error: bool) -> None:
    """Toggles the red 'invalid' border on a QLineEdit by flipping a dynamic
    property that the stylesheet above keys off (QSS needs a re-polish to
    notice a property change at runtime).

    This is a small, stand-alone helper function (not a method) because it
    doesn't belong to any single class - several unrelated widgets across
    the wizard call it, so it lives at module level instead of being tied
    to one object's internal state.
    """
    edit.setProperty("fieldState", "error" if is_error else "")
    edit.style().unpolish(edit)
    edit.style().polish(edit)
