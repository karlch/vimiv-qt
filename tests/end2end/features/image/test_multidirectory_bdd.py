# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest_bdd as bdd

from vimiv.imutils import filelist


bdd.scenarios("multidirectory.feature")


@bdd.then(bdd.parsers.parse("the image number {number:d} should be {basename}"))
def check_image_name_at_position(number, basename):
    image = filelist._paths[number - 1]
    assert os.path.basename(image) == basename
