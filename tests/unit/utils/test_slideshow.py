# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for utils.slideshow."""

import pytest

from vimiv.utils import slideshow


@pytest.fixture
def slides(mocker, cleansetup):
    mocker.patch("vimiv.gui.statusbar.update")
    s = slideshow.Slideshow()
    s.setInterval(1)  # Shorten waiting time
    yield s
    s.stop()


def test_toggle_slideshow(slides):
    slides.slideshow(0)
    assert slides.isActive()
    slides.slideshow(0)
    assert not slides.isActive()


def test_slideshow_emits_next_im_signal(slides, qtbot):
    with qtbot.waitSignal(slides.next_im, timeout=10):
        slides.slideshow(0)


def test_slideshow_set_delay_via_count(slides):
    slides.slideshow(2)
    assert slides.interval() == 2000
