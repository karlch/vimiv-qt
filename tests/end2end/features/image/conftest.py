# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv import imutils

try:
    import piexif
except ImportError:
    piexif = None


@pytest.fixture()
def exif_content():
    yield {
        "0th": {
            piexif.ImageIFD.Make: b"vimiv-testsuite",
            piexif.ImageIFD.Model: b"image-viewer",
            piexif.ImageIFD.Copyright: b"vimiv-AUTHORS-2020",
        },
        "Exif": {piexif.ExifIFD.ExposureTime: (1, 200)},
    }


@pytest.fixture()
def handler():
    yield imutils._ImageFileHandler.instance


@bdd.when("I add exif information")
def add_exif_information(handler, exif_content):
    assert piexif is not None, "piexif required to add exif information"
    path = handler._path
    exif_dict = piexif.load(path)
    for ifd, ifd_dict in exif_content.items():
        for key, value in ifd_dict.items():
            exif_dict[ifd][key] = value
    piexif.insert(piexif.dump(exif_dict), path)
