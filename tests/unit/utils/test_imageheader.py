# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2023-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.imageheader."""

from PyQt5.QtGui import QPixmap

import pytest


from vimiv.utils import imageheader

SUPPORTED_IMAGE_FORMATS = ["jpg", "png", "pbm", "pgm", "ppm", "bmp"]


def create_image(filename: str, *, size=(300, 300)):
    QPixmap(*size).save(filename)


@pytest.mark.parametrize("imagetype", SUPPORTED_IMAGE_FORMATS)
def test_test(qtbot, tmp_path, imagetype):
    name = f"img.{imagetype}"
    filename = str(tmp_path / name)
    create_image(filename)
    assert imageheader.detect(filename) == imagetype
