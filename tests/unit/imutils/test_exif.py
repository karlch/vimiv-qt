# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
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
    assert exif.check_exif_dependancy(default) == exif._ExifHandlerBase


@pytest.mark.parametrize(
    "methodname, args",
    (
        ("copy_exif", ("dest.jpg",)),
        ("exif_date_time", ()),
        ("get_formatted_exif", ([],)),
        ("get_keys", ()),
    ),
)
def test_handler_base_raises(methodname, args):
    handler = exif._ExifHandlerBase()
    method = getattr(handler, methodname)
    with pytest.raises(exif.UnsupportedExifOperation):
        method(*args)


@pytest.mark.parametrize(
    "handler, expected_msg",
    (
        (exif.ExifHandler, "not supported by pyexiv2"),
        (exif._ExifHandlerPiexif, "not supported by piexif"),
        (exif._ExifHandlerBase, "not supported. Please install"),
    ),
)
def test_handler_exception_customization(handler, expected_msg):
    with pytest.raises(exif.UnsupportedExifOperation, match=expected_msg):
        handler.raise_exception("test operation")
