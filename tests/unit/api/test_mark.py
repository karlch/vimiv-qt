# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.api._mark."""

import pytest

from vimiv import api


@pytest.fixture
def mark(mocker):
    api.mark.marked = mocker.Mock()
    api.mark.unmarked = mocker.Mock()
    mocker.patch("vimiv.utils.files.is_image", return_value=True)
    yield api.mark
    api.mark._marked.clear()
    api.mark._last_marked.clear()


def test_mark_single_image(mark):
    mark.mark(["image"])
    assert "image" in mark._marked
    assert mark.marked.called_once_with("image")


def test_mark_multiple_images(mark):
    mark.mark(["image1", "image2"])
    assert "image1" in mark._marked
    assert "image2" in mark._marked
    assert mark.marked.called_with("image1")
    assert mark.marked.called_with("image2")


def test_toggle_mark(mark):
    mark.mark(["image"])
    mark.mark(["image"])
    assert "image" not in mark._marked
    assert mark.unmarked.called_once_with("image")


def test_mark_clear(mark):
    mark.mark(["image"])
    mark.mark_clear()
    assert "image" not in mark._marked
    assert mark.unmarked.called_once_with("image")


def test_mark_restore(mark):
    mark.mark(["image"])
    mark.mark_clear()
    mark.mark_restore()
    assert "image" in mark._marked
    assert mark.marked.called_with("image")
