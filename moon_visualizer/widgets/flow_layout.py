"""
widgets/flow_layout.py
------------------------
A small reusable Qt layout that wraps its child widgets onto additional
rows as the available width shrinks, instead of overflowing or getting
squeezed the way QHBoxLayout does. Used for chip rows (quick-pick
locations, quick timezones) so they stay readable and click-able in
narrower panels/columns (e.g. the wizard's location step's side form,
or the Quick Settings popup) instead of spilling off the edge.

Adapted from Qt's own "Flow Layout" C++ example, translated to PySide6.
"""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class FlowLayout(QtWidgets.QLayout):
    """
    A layout that lays its items out left-to-right, wrapping onto a new
    row whenever the next item would no longer fit.

    # OOP concept: INHERITANCE + POLYMORPHISM (Qt layout interface)
    # -------------------------------------------------------------------
    # FlowLayout inherits QLayout and overrides its virtual geometry
    # methods (addItem, count, itemAt, takeAt, expandingDirections,
    # hasHeightForWidth, heightForWidth, setGeometry, sizeHint,
    # minimumSize). Every other Qt layout (QVBoxLayout, QGridLayout, ...)
    # honours that same abstract contract - this is what lets FlowLayout
    # be dropped into `addLayout()` calls anywhere a regular layout
    # would go, with the rest of the app never needing to know it's a
    # custom implementation instead of a built-in one.
    """

    def __init__(self, parent=None, margin: int = 0, h_spacing: int = 8, v_spacing: int = 8) -> None:
        super().__init__(parent)
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._items: list[QtWidgets.QLayoutItem] = []
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self) -> None:
        while self.count():
            self.takeAt(0)

    def addItem(self, item: QtWidgets.QLayoutItem) -> None:
        self._items.append(item)

    def horizontalSpacing(self) -> int:
        return self._h_spacing

    def verticalSpacing(self) -> int:
        return self._v_spacing

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self) -> QtCore.Qt.Orientations:
        return QtCore.Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QtCore.QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QtCore.QRect) -> None:
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QtCore.QSize:
        return self.minimumSize()

    def minimumSize(self) -> QtCore.QSize:
        size = QtCore.QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect: QtCore.QRect, test_only: bool) -> int:
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        x, y = effective_rect.x(), effective_rect.y()
        line_height = 0

        for item in self._items:
            space_x, space_y = self._h_spacing, self._v_spacing
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom
