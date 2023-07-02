# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2023-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.imageheader."""

from PyQt5.QtGui import QPixmap, QImageReader

import pytest


from vimiv.utils import imageheader

# Image types which QPixmap is capable of creating, and not what is supported by vimiv!
SUPPORTED_IMAGE_FORMATS = ["jpg", "png", "pbm", "pgm", "ppm", "bmp"]


@pytest.fixture()
def mockimageheader(mocker):
    """Fixture to mock imageheader._registry and QImageReader supportedImageFormats."""
    mocker.patch.object(
        QImageReader, "supportedImageFormats", return_value=SUPPORTED_IMAGE_FORMATS
    )
    yield mocker.patch("vimiv.utils.imageheader._registry", [])


@pytest.fixture()
def tmpfile(tmp_path):
    path = tmp_path / "anything"
    path.touch()
    yield str(path)


def create_image(filename: str, *, size=(300, 300)):
    QPixmap(*size).save(filename)


@pytest.mark.parametrize("imagetype", SUPPORTED_IMAGE_FORMATS)
def test_test(qtbot, tmp_path, imagetype):
    name = f"img.{imagetype}"
    filename = str(tmp_path / name)
    create_image(filename)
    assert imageheader.detect(filename) == imagetype


def _check_dummy(h):
    """Dummy image file check that always returns True."""
    return True


@pytest.mark.parametrize("name", SUPPORTED_IMAGE_FORMATS)
def test_register_supported_format(mockimageheader, tmpfile, name):
    imageheader.register(name, _check_dummy)
    assert mockimageheader, "No test added by add image format"
    assert imageheader.detect(tmpfile) == name


def test_register_unsupported_format(mockimageheader, tmpfile):
    imageheader.register("not_a_format", _check_dummy)
    assert imageheader.detect(tmpfile) is None
    assert not mockimageheader, "Unsupported test not removed"
