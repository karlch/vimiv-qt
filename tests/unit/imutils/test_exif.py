# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.exif."""

import pytest

from vimiv.imutils import exif


@pytest.fixture(params=[exif.ExifHandler, exif._ExifHandlerPiexif])
def exif_handler(request):
    """Parametrized pytest fixture to yield the different exif handlers."""
    yield request.param


def test_check_exif_dependency():
    default = None
    assert exif.check_exif_dependancy(default) == default


def test_check_exif_dependency_piexif(piexif):
    default = None
    assert exif.check_exif_dependancy(default) == exif._ExifHandlerPiexif


def test_check_exif_dependency_noexif(noexif):
    default = None
    assert exif.check_exif_dependancy(default) == exif._ExifHandlerNoExif


@pytest.mark.parametrize(
    "methodname", ("copy_exif", "exif_date_time", "get_formatted_exif")
)
def test_handler_noexif(methodname):
    handler = exif._ExifHandlerNoExif()
    method = getattr(handler, methodname)
    with pytest.raises(exif.NoExifSupport):
        method()
