# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import re

import pytest
import pytest_bdd as bdd

import vimiv.gui.crop_widget
from vimiv.qt.core import Qt, QPoint
from vimiv.qt.widgets import QApplication


bdd.scenarios("crop.feature")


def find_crop_widgets(image):
    return image.findChildren(vimiv.gui.crop_widget.CropWidget)


@pytest.fixture()
def crop(image):
    """Fixture to retrieve the current instance of the crop widget."""
    widgets = find_crop_widgets(image)
    assert len(widgets) == 1, "Wrong number of crop wigets found"
    return widgets[0]


@pytest.fixture()
def ensure_moving():
    QApplication.setOverrideCursor(Qt.ClosedHandCursor)
    yield
    QApplication.restoreOverrideCursor()


@bdd.when(bdd.parsers.parse("I press '{keys}' in the crop widget"))
def press_key_crop(keypress, crop, keys):
    keypress(crop, keys)


@bdd.then(bdd.parsers.parse("there should be {number:d} crop widgets"))
@bdd.then(bdd.parsers.parse("there should be {number:d} crop widget"))
def check_number_of_crop_widgets(qtbot, image, number):
    def check():
        assert len(find_crop_widgets(image)) == number

    qtbot.waitUntil(check)


@bdd.when(bdd.parsers.parse("I drag the crop widget by {dx:d}+{dy:d}"))
@bdd.when("I drag the crop widget by <dx>+<dy>")
def drag_crop_widget(qtbot, mousedrag, crop, dx, dy):
    dx = int(int(dx) * crop.image.zoom_level)
    dy = int(int(dy) * crop.image.zoom_level)

    start = QPoint(crop.width() // 2, crop.height() // 2)
    mousedrag(crop, start=start, diff=QPoint(dx, dy))


@bdd.then(bdd.parsers.parse("the crop rectangle should be {geometry}"))
@bdd.then("the crop rectangle should be <geometry>")
def check_crop_rectangle(crop, geometry):
    match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", geometry)
    assert match is not None, "Invalid geometry passed"
    width, height, x, y = match.groups()
    rect = crop.crop_rect()
    assert int(width) == pytest.approx(rect.width(), abs=1)
    assert int(height) == pytest.approx(rect.height(), abs=1)
    assert int(x) == pytest.approx(rect.x(), abs=1)
    assert int(y) == pytest.approx(rect.y(), abs=1)
