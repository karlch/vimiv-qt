# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.exif."""

import pytest

from vimiv.imutils import exif


@pytest.fixture
def no_piexif():
    initial_piexif = exif.piexif
    exif.piexif = None
    yield
    exif.piexif = initial_piexif


def test_check_piexif(no_piexif):
    @exif.check_piexif(return_value="")
    def dummy_func():
        return "this should never be returned"

    assert dummy_func() == ""
