# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

try:
    import piexif
except ImportError:
    piexif = None

from vimiv import imutils


bdd.scenarios("write.feature")


@pytest.fixture()
def handler():
    yield imutils._ImageFileHandler.instance


@pytest.fixture()
def exif_content():
    yield {
        "0th": {piexif.ImageIFD.Make: b"vimiv-testsuite"},
        "Exif": {piexif.ExifIFD.Sharpness: 65535},
    }


@bdd.when(bdd.parsers.parse("I write the image to {name}"))
@bdd.when("I write the image to <name>")
def write_image(handler, name):
    handler.write_pixmap(
        handler._current_pixmap.get(),
        path=name,
        original_path=handler._path,
        parallel=False,
    )


@bdd.when("I add exif information")
def add_exif_information(handler, exif_content):
    assert piexif is not None, "piexif required to add exif information"
    path = handler._path
    exif_dict = piexif.load(path)
    for ifd, ifd_dict in exif_content.items():
        for key, value in ifd_dict.items():
            exif_dict[ifd][key] = value
    piexif.insert(piexif.dump(exif_dict), path)


@bdd.then(bdd.parsers.parse("the image {name} should contain exif information"))
def check_exif_information(exif_content, name):
    exif_dict = piexif.load(name)
    for ifd, ifd_dict in exif_content.items():
        for key, value in ifd_dict.items():
            assert exif_dict[ifd][key] == value
