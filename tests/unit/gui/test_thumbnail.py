# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2022 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.gui.thumbnail."""

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

import pytest

from vimiv.gui.thumbnail import ThumbnailItem


@pytest.fixture()
def item(mocker):
    """Fixture to retrieve a vanilla ThumbnailItem."""
    ThumbnailItem._default_icon = None
    mocker.patch.object(ThumbnailItem, "create_default_icon", return_value=QIcon())
    yield ThumbnailItem


def test_create_default_pixmap_once(item):
    """Ensure the default thumbnail icon is only created once."""
    size_hint = QSize(128, 128)
    for index in range(5):
        item(None, index, name="image.jpg", size_hint=size_hint)
    item.create_default_icon.assert_called_once()
