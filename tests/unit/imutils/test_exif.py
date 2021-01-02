# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.exif."""

import pytest

from vimiv.imutils import exif


@pytest.fixture
def no_pyexiv2():
    initial_pyexiv2 = exif.pyexiv2
    exif.pyexiv2 = None
    yield
    exif.pyexiv2 = initial_pyexiv2


@pytest.fixture
def no_piexif():
    exif.pyexiv2 = None
    initial_piexif = exif.piexif
    exif.piexif = None
    yield
    exif.piexif = initial_piexif


def test_check_pyexiv2(no_pyexiv2):
    @exif.check_exif_dependancy
    class DummyClass:
        def __init__(self, *args):
            pass

    assert isinstance(DummyClass(), (exif._ExifHandlerPiexif, exif._ExifHandlerNoExif))


def test_check_piexif(no_piexif):
    @exif.check_exif_dependancy
    class DummyClass:
        def __init__(self, *args):
            pass

    assert isinstance(DummyClass(), exif._ExifHandlerNoExif)
