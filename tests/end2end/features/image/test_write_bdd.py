# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

try:
    import piexif
except ImportError:
    piexif = None


bdd.scenarios("write.feature")


@bdd.when(bdd.parsers.parse("I write the image to {name}"))
@bdd.when("I write the image to <name>")
def write_image(handler, name):
    handler.write_pixmap(
        handler._edit_handler.pixmap,
        path=name,
        original_path=handler._path,
        parallel=False,
    )


@bdd.then(bdd.parsers.parse("the image {name} should contain exif information"))
def check_exif_information(exif_content, name):
    exif_dict = piexif.load(name)
    for ifd, ifd_dict in exif_content.items():
        for key, value in ifd_dict.items():
            assert exif_dict[ifd][key] == value
