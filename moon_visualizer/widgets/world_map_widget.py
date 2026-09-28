"""
widgets/world_map_widget.py
------------------------------
WorldMapWidget - a small self-contained "pick a point on Earth" widget.

It paints a stylised equirectangular world map (simplified continent
outlines - not a survey-accurate atlas, just enough visual context to
click on) and lets the user set the observer's latitude and longitude by
clicking or dragging on it, instead of typing numbers into two text
fields blind.

Because a hand-drawn outline can never fit every country precisely
(that's what made the old version hard to use for smaller or oddly
shaped countries), the *reliable* way to reach an exact spot is the
companion search box in `LocationPickerWidget` - this widget's job is
just to give that pick some visual context and to stay usable on its
own for "close enough, click roughly here" adjustments.
"""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from ..geo import FAVORITE_LOCATIONS, WorldLocation
from ..theme import Theme

# Map aspect ratio is always 2:1 for an equirectangular projection
# (360 degrees of longitude across, 180 degrees of latitude tall).
_MAP_ASPECT = 2.0

# Simplified continent/landmass outlines: (longitude, latitude) pairs.
# More densely sampled than a first pass at this ("just enough dots to
# vaguely suggest a shape") so the silhouettes are actually recognisable
# at a glance, and split into more separate pieces (Greenland, Madagascar,
# Japan, the British Isles, New Zealand, insular Southeast Asia, ...)
# instead of lumping everything into six giant blobs where whole regions
# had nowhere to click at all. Still a stylised approximation, not
# precise geographic/survey data - exact placement is what the search
# box and lat/lon fields are for.
_LANDMASSES: list[list[tuple[float, float]]] = [
    # North America (mainland + Alaska)
    [(-168, 66), (-161, 70.5), (-149, 70.5), (-141, 69.5), (-128, 70),
     (-120, 69), (-105, 68.5), (-95, 68), (-85, 67), (-80, 62), (-75, 58),
     (-65, 55), (-60, 50), (-64, 46), (-70, 44), (-67, 45), (-70, 41),
     (-74, 40), (-76, 37), (-76, 34), (-80, 32), (-81, 25), (-83, 29),
     (-88, 30), (-94, 29.5), (-97, 26), (-97, 20), (-90, 16), (-92, 14),
     (-105, 20.5), (-110, 24), (-115, 27), (-114, 31), (-117, 32.5),
     (-124, 40.5), (-124, 46), (-123, 49), (-130, 55), (-135, 58.5),
     (-141, 60), (-150, 60), (-158, 58.5), (-162, 59), (-166, 60.5),
     (-168, 66)],
    # South America
    [(-77, 8), (-72, 11), (-71, 9), (-77, 3), (-79, -3), (-80, -6),
     (-81, -12), (-77, -14), (-71, -18), (-70, -23), (-70, -30), (-71, -37),
     (-73, -42), (-74, -46), (-73, -50), (-69, -52), (-68, -55), (-65, -55),
     (-66, -51), (-62, -45), (-58, -38), (-57, -35), (-53, -34), (-48, -25),
     (-40, -15), (-38, -13), (-35, -8), (-39, -3), (-44, -1), (-48, 1),
     (-51, 4), (-58, 8), (-61, 8), (-67, 9), (-73, 11), (-77, 8)],
    # Africa
    [(-17, 15), (-16, 12.5), (-11, 7), (-10, 5), (-4, 5), (2, 5), (9, 4.5),
     (9, -1), (8, -5), (12, -5.5), (13.5, -12), (12, -17), (13, -22),
     (16, -28), (18, -34), (20, -34.8), (25, -33.9), (28, -33), (30, -29),
     (32, -26), (33, -22), (35, -18), (40, -16), (40, -11), (44, -1),
     (48, -12), (51, -12), (51, 4), (49, 11), (45, 11), (43, 12), (43, 5),
     (41, 8), (39, 11), (43, 14), (40, 16), (38, 18), (37, 23), (35, 28),
     (33, 27), (33, 31), (31, 31.5), (25, 31.5), (25, 22), (22, 22),
     (14, 22), (10, 20), (10, 13), (5, 11), (3, 11), (-2, 6), (-6, 5),
     (-9, 5), (-11, 6.5), (-16, 12.5), (-17, 15)],
    # Madagascar
    [(49.5, -12.3), (50.2, -15.2), (49.9, -18), (47.5, -25.3), (44.5, -24.9),
     (43.3, -22), (43.7, -19), (44.4, -16.2), (47.9, -12.3), (49.5, -12.3)],
    # Europe (mainland, excl. British Isles)
    [(-9.5, 43), (-9, 39), (-7.5, 37), (-2, 36.7), (3, 39.5), (2, 41.5),
     (7.5, 43.7), (10, 44), (12.5, 41.9), (15.9, 41.2), (18.5, 40),
     (20, 39.5), (23, 38), (24, 40), (26.5, 40), (26, 41.5), (29, 41),
     (30.5, 45.5), (36.5, 45.3), (39, 47), (38.5, 49), (39, 51.5), (40, 54),
     (35, 55.8), (30, 59.8), (30.3, 63), (28, 65), (24, 66), (21, 68.5),
     (17, 69), (14, 67.9), (13, 65.6), (10.4, 63.4), (5.3, 61), (5, 58.9),
     (8, 58), (10.5, 57.7), (8, 56.5), (8.5, 55), (8, 53.5), (4, 51.5),
     (1.5, 50.9), (-1.5, 49.7), (-4.5, 48.3), (-2, 47.3), (-1.8, 46),
     (-4, 43.5), (-9.5, 43)],
    # British Isles
    [(-5, 58.6), (-3, 58.6), (-1.8, 57.7), (-2, 56.5), (0.2, 52.9),
     (1.3, 51.4), (-1, 50.7), (-4.5, 50.2), (-5.7, 50), (-4.2, 51.2),
     (-3, 51.5), (-3.4, 52.8), (-4.8, 53.4), (-3, 53.5), (-3, 55),
     (-5.1, 55), (-5, 58.6)],
    [(-6, 55.2), (-8, 54.5), (-9.9, 53.4), (-9.7, 51.5), (-8.2, 51.4),
     (-6, 52.2), (-6.2, 53.9), (-6, 55.2)],  # Ireland
    # Asia (mainland, incl. Middle East and Arabian Peninsula)
    [(27, 41.3), (29, 41), (35, 36), (36, 33.5), (35, 31.5), (34.9, 29.5),
     (36, 27), (39, 21.5), (42, 16.5), (43.2, 12.5), (45, 12.8), (48, 14),
     (52, 19), (56.4, 26.6), (56.3, 25.4), (58.9, 23.6), (61.8, 25),
     (63, 25.2), (66.8, 24.7), (69.5, 22.5), (72.8, 20.5), (73, 15.5),
     (76, 8.5), (77.5, 8), (80.3, 6.9), (80.3, 9.8), (78.2, 10.3),
     (80.2, 13.5), (80.3, 20.3), (86.5, 21.5), (91.8, 22.3), (92.3, 20.7),
     (94, 16.5), (98.4, 8.4), (100.1, 6.7), (103.4, 1.3), (104.9, 1),
     (104.9, 10.8), (106.7, 10.4), (109.3, 12.9), (108, 16.1), (107.9, 20.9),
     (109.5, 21.5), (108.6, 21.7), (110, 21), (117, 23.5), (121, 25.3),
     (120, 30), (122, 31), (121.5, 33), (124, 37), (127.5, 39), (129.4, 35),
     (130, 33.6), (131, 34), (132, 34.5), (135, 35), (140.9, 37.3),
     (141.4, 40.5), (140, 43.5), (141.9, 45.3), (143, 44), (145.8, 43.4),
     (140, 42), (139.8, 46.9), (142.7, 47.6), (144, 48.9), (140, 51.6),
     (135.3, 52.9), (137, 54.5), (135, 55.5), (140, 59), (150, 59.7),
     (156.8, 61.4), (162.9, 60.3), (170, 65), (177, 65), (179, 68),
     (175, 68), (170, 70), (160, 71), (150, 72.4), (140, 73.5),
     (130, 72.8), (110, 73.5), (98, 73), (90, 72), (79, 73), (68, 72),
     (60, 70), (58, 67.5), (49, 66.5), (44, 66.7), (41.5, 64.9), (35, 66.7),
     (33, 67.6), (33, 64.9), (30, 64.9), (28.6, 60.5), (27, 41.3)],
    # Insular Southeast Asia (Sumatra/Java/Borneo cluster, simplified)
    [(95.3, 5.6), (97.9, 3.8), (100.4, 2.1), (103.5, -0.3), (105.9, -5.9),
     (104.6, -6.6), (99.7, -3.4), (96, 0.2), (95.3, 5.6)],  # Sumatra
    [(105.3, -6.8), (106.9, -6.1), (110.4, -6.9), (114.5, -7.7),
     (114.6, -8.6), (111, -8.4), (108.4, -7.8), (105.3, -6.8)],  # Java
    [(109, 7.1), (117, 7.3), (119, 4.2), (117, -1), (116, -4), (114, -4.1),
     (109.7, -2.9), (109, 1.5), (109, 7.1)],  # Borneo
    [(120, 10.3), (122, 18.5), (124, 18.6), (125, 12.7), (123.9, 9),
     (122, 6.3), (120, 10.3)],  # Philippines
    # Australia
    [(113.2, -22), (113.7, -26.6), (115.7, -32), (117.9, -35), (121.9, -34),
     (124.3, -33.8), (129, -31.5), (131.5, -31.5), (133.8, -32.5),
     (135.9, -34.5), (137.8, -35.2), (139.9, -37.8), (140.1, -38.4),
     (144.9, -38.4), (146.8, -39), (148.4, -37.9), (150, -37), (150.4, -35),
     (153.1, -30.4), (153.2, -25.5), (150.5, -22.5), (147, -19.5),
     (145.8, -16.7), (143, -13), (141.5, -12.2), (137, -12), (135.9, -11.9),
     (136.6, -13.7), (135.5, -14.9), (132.5, -12), (130, -12.4),
     (129.1, -14.9), (126.9, -14.1), (124.4, -16.4), (122.2, -18),
     (114.9, -21.8), (113.2, -22)],
    # New Zealand
    [(174.6, -36.8), (176.9, -37.7), (178.5, -38.7), (177.9, -39.5),
     (176.9, -40.3), (174.9, -41.3), (173.8, -41.3), (172.6, -40.5),
     (172.7, -38.6), (174.6, -36.8)],  # North Island
    [(173.2, -40.9), (172, -41.5), (170.2, -43.4), (168.4, -44.9),
     (166.5, -45.5), (167.2, -46.6), (169.1, -46.4), (171.4, -44.2),
     (173.3, -41.6), (173.2, -40.9)],  # South Island
    # Greenland
    [(-52, 60), (-45, 61.5), (-42, 60.2), (-40.5, 65), (-37, 70), (-24, 71.5),
     (-20, 75), (-18, 80), (-30, 82.5), (-45, 82.5), (-58, 79), (-65, 76),
     (-68, 72), (-56, 66), (-54, 63), (-52, 60)],
]

# The 6 hand-picked favourites (see geo/world_locations.py) still get a
# dedicated dot + hover label on the map for one-click access; every
# other country is reachable through the search box in LocationPickerWidget.
PRESET_CITIES: list[WorldLocation] = FAVORITE_LOCATIONS


class WorldMapWidget(QtWidgets.QWidget):
    """
    A clickable equirectangular world map for picking a latitude/longitude.

    # OOP concept: ENCAPSULATION + COMPOSITION OVER RE-IMPLEMENTATION
    # -----------------------------------------------------------------
    # Everything about *how* a click becomes a (lat, lon) pair - the
    # projection math, the landmass painting, the marker - is hidden
    # inside this one widget. Whoever uses it (LocationPickerWidget,
    # shared by QuickSettingsDialog and the wizard's LocationStepPage)
    # only ever talks to it through `location_picked`, `set_location()`
    # and `current_location()`; none of the pixel math leaks out.

    Emits `location_picked(lat, lon)` every time the user clicks or drags
    to choose a new point - NOT on every tiny mouse-move pixel, but once
    per resulting (rounded) coordinate change, so callers can hook it
    straight up to a live-updating summary/timezone lookup.
    """

    location_picked = QtCore.Signal(float, float)
    preset_picked = QtCore.Signal(str, float, float, str)  # name, lat, lon, tz

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(320, 170)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setMouseTracking(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._lat = 6.9271
        self._lon = 79.8612
        self._label = ""
        self._hover_preset: WorldLocation | None = None
        self._map_rect = QtCore.QRectF()

    # -- public API -------------------------------------------------------

    def set_location(self, latitude_deg: float, longitude_deg: float, label: str = "") -> None:
        """Reposition the marker WITHOUT emitting location_picked - used
        when some other widget (the search box / lat/lon spin boxes) is
        the source of truth for this change, to avoid a feedback loop.
        `label`, when given, is shown next to the marker (e.g. the name
        the user just searched for)."""
        self._lat = max(-90.0, min(90.0, latitude_deg))
        self._lon = max(-180.0, min(180.0, longitude_deg))
        self._label = label
        self.update()

    def current_location(self) -> tuple[float, float]:
        return self._lat, self._lon

    # -- Qt geometry --------------------------------------------------------
    #
    # Deliberately NOT overriding heightForWidth()/hasHeightForWidth() here.
    # Qt's height-for-width propagation through nested layouts (this widget
    # -> LocationPickerWidget's QVBoxLayout -> the wizard page's layout ->
    # a QStackedWidget) is unreliable in practice and was exactly why the
    # map used to render tiny even with acres of free space around it: Qt
    # kept sizing it to a small heightForWidth-derived hint instead of
    # letting its "stretch=1" actually claim the leftover room. Declaring
    # this a PLAIN Expanding/Expanding widget lets normal stretch-based
    # layout math give it as much space as its container can spare; the
    # widget itself still always draws a correct 2:1 map, letterboxed
    # inside whatever rectangle it ends up with (see _compute_map_rect),
    # so nothing about the aspect ratio is lost - it just now actually
    # gets to be big.

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(700, 350)

    # -- projection helpers ---------------------------------------------------

    def _compute_map_rect(self) -> QtCore.QRectF:
        """The map is always drawn 2:1, letterboxed inside whatever space
        the layout actually gives this widget."""
        w, h = self.width(), self.height()
        if w / _MAP_ASPECT <= h:
            map_w, map_h = w, w / _MAP_ASPECT
        else:
            map_h, map_w = h, h * _MAP_ASPECT
        x = (w - map_w) / 2
        y = (h - map_h) / 2
        return QtCore.QRectF(x, y, map_w, map_h)

    def _lonlat_to_point(self, lon: float, lat: float) -> QtCore.QPointF:
        r = self._map_rect
        x = r.left() + (lon + 180.0) / 360.0 * r.width()
        y = r.top() + (90.0 - lat) / 180.0 * r.height()
        return QtCore.QPointF(x, y)

    def _point_to_lonlat(self, pos: QtCore.QPointF) -> tuple[float, float] | None:
        r = self._map_rect
        if r.width() <= 0 or r.height() <= 0:
            return None
        lon = (pos.x() - r.left()) / r.width() * 360.0 - 180.0
        lat = 90.0 - (pos.y() - r.top()) / r.height() * 180.0
        lon = max(-180.0, min(180.0, lon))
        lat = max(-90.0, min(90.0, lat))
        return lon, lat

    # -- painting -----------------------------------------------------------

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # noqa: N802 (Qt override)
        self._map_rect = self._compute_map_rect()
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        self._draw_ocean(painter)
        self._draw_graticule(painter)
        self._draw_landmasses(painter)
        self._draw_presets(painter)
        self._draw_marker(painter)
        self._draw_border(painter)

        painter.end()

    def _draw_ocean(self, painter: QtGui.QPainter) -> None:
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(Theme.BG_PANEL_2))
        painter.drawRoundedRect(self._map_rect, 6, 6)

    def _draw_graticule(self, painter: QtGui.QPainter) -> None:
        pen = QtGui.QPen(QtGui.QColor(Theme.BORDER))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        for lon in range(-180, 181, 30):
            p1 = self._lonlat_to_point(lon, 90)
            p2 = self._lonlat_to_point(lon, -90)
            painter.drawLine(p1, p2)
        for lat in range(-90, 91, 30):
            p1 = self._lonlat_to_point(-180, lat)
            p2 = self._lonlat_to_point(180, lat)
            painter.drawLine(p1, p2)
        # Equator drawn a little brighter as a visual anchor.
        eq_pen = QtGui.QPen(QtGui.QColor(Theme.ACCENT_SOFT))
        eq_pen.setWidthF(1.4)
        painter.setPen(eq_pen)
        painter.drawLine(self._lonlat_to_point(-180, 0), self._lonlat_to_point(180, 0))

    def _draw_landmasses(self, painter: QtGui.QPainter) -> None:
        painter.setPen(QtGui.QPen(QtGui.QColor(Theme.BG_PANEL), 0.8))
        painter.setBrush(QtGui.QColor(Theme.ACCENT_SOFT))
        for outline in _LANDMASSES:
            polygon = QtGui.QPolygonF([self._lonlat_to_point(lon, lat) for lon, lat in outline])
            painter.drawPolygon(polygon)

    def _draw_presets(self, painter: QtGui.QPainter) -> None:
        for loc in PRESET_CITIES:
            pt = self._lonlat_to_point(loc.longitude_deg, loc.latitude_deg)
            is_hover = self._hover_preset is not None and self._hover_preset.name == loc.name
            radius = 5.0 if is_hover else 3.5
            painter.setPen(QtGui.QPen(QtGui.QColor(Theme.BG), 1.2))
            painter.setBrush(QtGui.QColor(Theme.ACCENT if is_hover else Theme.TEXT_DIM))
            painter.drawEllipse(pt, radius, radius)
            if is_hover:
                painter.setPen(QtGui.QColor(Theme.TEXT))
                painter.drawText(pt + QtCore.QPointF(8, 4), loc.name)

    def _draw_marker(self, painter: QtGui.QPainter) -> None:
        pt = self._lonlat_to_point(self._lon, self._lat)
        painter.setPen(QtGui.QPen(QtGui.QColor(Theme.ACCENT), 2))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawLine(pt.x() - 9, pt.y(), pt.x() + 9, pt.y())
        painter.drawLine(pt.x(), pt.y() - 9, pt.x(), pt.y() + 9)
        painter.setPen(QtGui.QPen(QtGui.QColor(Theme.BG), 1.5))
        painter.setBrush(QtGui.QColor(Theme.ACCENT))
        painter.drawEllipse(pt, 5.0, 5.0)
        if self._label:
            painter.setPen(QtGui.QColor(Theme.TEXT))
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(pt + QtCore.QPointF(10, -8), self._label)

    def _draw_border(self, painter: QtGui.QPainter) -> None:
        pen = QtGui.QPen(QtGui.QColor(Theme.BORDER))
        pen.setWidthF(1.2)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRoundedRect(self._map_rect, 6, 6)

    # -- mouse interaction -----------------------------------------------------

    def _preset_at(self, pos: QtCore.QPointF) -> WorldLocation | None:
        for loc in PRESET_CITIES:
            pt = self._lonlat_to_point(loc.longitude_deg, loc.latitude_deg)
            if (pt - pos).manhattanLength() <= 9:
                return loc
        return None

    def _pick(self, pos: QtCore.QPointF) -> None:
        result = self._point_to_lonlat(pos)
        if result is None:
            return
        lon, lat = result
        self._lat, self._lon = lat, lon
        self._label = ""
        self.update()
        self.location_picked.emit(round(lat, 4), round(lon, 4))

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:  # noqa: N802
        preset = self._preset_at(event.position())
        if preset is not None:
            self._lat, self._lon = preset.latitude_deg, preset.longitude_deg
            self._label = preset.name
            self.update()
            self.preset_picked.emit(preset.name, preset.latitude_deg, preset.longitude_deg, preset.timezone)
            return
        self._pick(event.position())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:  # noqa: N802
        if event.buttons() & QtCore.Qt.LeftButton:
            self._pick(event.position())
            return
        hovered = self._preset_at(event.position())
        if hovered != self._hover_preset:
            self._hover_preset = hovered
            self.setToolTip(hovered.name if hovered else "")
            self.update()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:  # noqa: N802
        self._map_rect = self._compute_map_rect()
        super().resizeEvent(event)
