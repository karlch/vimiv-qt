# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest_bdd as bdd

from vimiv.imutils import imstorage


bdd.scenarios("imagedelete.feature")


@bdd.then(bdd.parsers.parse("the filelist should contain {number} images"))
def check_filelist_length(number):
    assert imstorage.total() == number


@bdd.then(bdd.parsers.parse("{basename} should not be in the filelist"))
def check_image_not_in_filelist(basename):
    abspath = os.path.abspath(basename)
    assert abspath not in imstorage._paths
