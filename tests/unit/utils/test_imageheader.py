# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.imageheader."""

import pytest

from vimiv.qt.gui import QPixmap, QImageReader, QImageWriter
from vimiv.utils import imageheader

# Formats that are detectable and not detectable by this module
DETECT_FORMATS = [format for format, _ in imageheader._registry]
NOT_DETECT_FORMATS = ["pdf", "svgz", "wbmp"]

# QT Formats that alias to others
QT_ALIAS_FORMATS = ["jpeg", "tif"]

# Formats that QT can create and that are also detectable
QT_WRITE_DETECT_FORMATS = [
    d.data().decode()
    for d in QImageWriter.supportedImageFormats()
    if d.data().decode() not in NOT_DETECT_FORMATS
    and d.data().decode() not in QT_ALIAS_FORMATS
    and d.data().decode() != "cur"  # CUR types created by QT are actually ICO?!
]

# Formats that QT can read
QT_READ_FORMATS = [
    d.data().decode()
    for d in QImageReader.supportedImageFormats()
    if d.data().decode() not in QT_ALIAS_FORMATS
]


@pytest.fixture()
def mockimageheader(mocker):
    """Fixture to mock imageheader._registry and QImageReader supportedImageFormats."""
    mocker.patch.object(
        QImageReader, "supportedImageFormats", return_value=QT_READ_FORMATS
    )
    yield mocker.patch("vimiv.utils.imageheader._registry", [])


def create_image(filename: str, *, size=(300, 300)):
    QPixmap(*size).save(filename)


@pytest.mark.parametrize("imagetype", QT_WRITE_DETECT_FORMATS)
def test_detect(qtbot, tmp_path, imagetype):
    """Only tests check functions for formats that QT can create samples for."""
    name = f"img.{imagetype}"
    filename = str(tmp_path / name)
    create_image(filename)
    assert imageheader.detect(filename) == imagetype


def _check_dummy(h, f):
    """Dummy image file check that always returns True."""
    return True


@pytest.mark.parametrize("name", QT_READ_FORMATS)
def test_register_supported_format(mockimageheader, tmpfile, name):
    imageheader.register(name, _check_dummy)
    assert mockimageheader, "No test added by add image format"
    assert imageheader.detect(tmpfile) == name


def test_register_unsupported_format(mockimageheader, tmpfile):
    """Test if check of invalid format gets removed after call to `detect`."""
    imageheader.register("not_a_format", _check_dummy)
    assert imageheader.detect(tmpfile) is None
    assert not mockimageheader, "Unsupported test not removed"


def test_register_unsupported_format_not_verify(mockimageheader, tmpfile):
    """Test if check of invalid remains when registered without verification."""
    dummy_format = "not_a_format"
    imageheader.register(dummy_format, _check_dummy, validate=False)
    assert imageheader.detect(tmpfile) == dummy_format
    assert (dummy_format, _check_dummy) in imageheader._registry


@pytest.mark.parametrize("name", QT_READ_FORMATS)
def test_full_support(name):
    """Tests if all formats readable by QT are also detected."""
    assert name in NOT_DETECT_FORMATS or name in DETECT_FORMATS, "Missing check"
