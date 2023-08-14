# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Integration tests related to editing images."""

import pytest

from vimiv.qt.gui import QPixmap, QColor

from vimiv.config import styles
from vimiv.imutils import edit_handler


WIDTH = 300
HEIGHT = 200
COLOR = QColor("#888888")


@pytest.fixture()
def edit(mocker, qtbot):
    mocker.patch("vimiv.api.signals")
    mocker.patch("vimiv.api.modes.Mode.close")
    mocker.patch.object(styles, "_style", styles.create_default())
    handler = edit_handler.EditHandler()
    handler._init_manipulate()
    handler.pixmap = QPixmap(WIDTH, HEIGHT)
    handler.pixmap.fill(COLOR)
    yield handler


@pytest.fixture()
def transform(edit):
    yield edit.transform


@pytest.fixture()
def manipulate(edit):
    edit.manipulate._enter()
    return edit.manipulate


def current_color(pixmap):
    image = pixmap.toImage()
    return QColor(image.pixel(0, 0))


def test_transform_applied(edit, transform):
    transform.rotate_command()
    assert edit.pixmap.width() == HEIGHT
    assert edit.pixmap.height() == WIDTH


def test_manipulate_applied(edit, manipulate):
    manipulate.increase(10)
    manipulate.accept()
    assert current_color(edit.pixmap) != COLOR


def test_manipulate_and_transform_iteratively(edit, transform, manipulate):
    transform.rotate_command()
    manipulate.increase(10)
    manipulate.accept()
    assert edit.pixmap.width() == HEIGHT
    assert edit.pixmap.height() == WIDTH
    assert current_color(edit.pixmap) != COLOR
    transform.rotate_command()
    assert edit.pixmap.height() == HEIGHT
    assert edit.pixmap.width() == WIDTH
