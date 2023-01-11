# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest
import pytest_bdd as bdd

from vimiv import imutils, utils

try:
    import piexif
except ImportError:
    piexif = None


@pytest.fixture()
def exif_content():
    return {
        "0th": {
            piexif.ImageIFD.Make: b"vimiv-testsuite",
            piexif.ImageIFD.Model: b"image-viewer",
            piexif.ImageIFD.Copyright: b"vimiv-AUTHORS-2020",
        },
        "Exif": {piexif.ExifIFD.ExposureTime: (1, 200)},
        "GPS": {piexif.GPSIFD.GPSAltitude: (1234, 1)},
    }


@pytest.fixture()
def handler():
    return imutils._ImageFileHandler.instance


@bdd.when("I add exif information")
def add_exif_information_bdd(add_exif_information, handler, exif_content):
    assert piexif is not None, "piexif required to add exif information"
    # Wait for thumbnail creation so we don't interfere with the current reading by
    # adding more bytes
    utils.Pool.wait(5000)
    add_exif_information(handler._path, exif_content)


@bdd.then(bdd.parsers.parse("the image number {number:d} should be {basename}"))
def check_image_name_at_position(number, basename):
    image = imutils.pathlist()[number - 1]
    assert os.path.basename(image) == basename
