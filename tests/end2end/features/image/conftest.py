# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Additional bdd steps for image tests."""

import pytest_bdd as bdd

from vimiv.imutils import imstorage


@bdd.then(bdd.parsers.parse("the image should have the index {index}"))
def check_image_index(index):
    assert imstorage.get_index() == index
