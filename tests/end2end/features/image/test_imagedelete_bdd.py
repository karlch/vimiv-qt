# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest_bdd as bdd

import vimiv.gui.image
from vimiv.imutils import filelist


bdd.scenarios("imagedelete.feature")


@bdd.then(bdd.parsers.parse("{basename} should not be in the filelist"))
def check_image_not_in_filelist(basename):
    abspath = os.path.abspath(basename)
    assert abspath not in filelist._paths


@bdd.then("the image widget should be empty")
def check_image_widget_empty(image):
    assert isinstance(image.widget(), vimiv.gui.image.Empty)
