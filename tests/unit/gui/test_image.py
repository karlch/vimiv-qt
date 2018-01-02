# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.gui.image."""

import pytest

from PyQt5.QtWidgets import QStackedLayout

from vimiv.gui import image


@pytest.fixture
def im(qtbot):
    """Set up image widget in qtbot."""
    scrollable_image = image.ScrollableImage(QStackedLayout())
    qtbot.addWidget(scrollable_image)
    my_im = image.Image(parent=scrollable_image)
    qtbot.addWidget(my_im)
    yield my_im


@pytest.mark.usefixtures("cleansetup")
class TestImage():

    def test_open_image(self, tmpimage, im):
        im.open(tmpimage)
        # TODO assertion


    def test_zoom_image(self, tmpimage, im):
        im.open(tmpimage)
        w_before = im.pixmap().width()
        im.zoom("in", 1)
        assert im.pixmap().width() > w_before
        im.zoom("out", 1)
        assert im.pixmap().width() == pytest.approx(w_before, rel=2)
