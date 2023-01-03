# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv.parser import geometry


@bdd.then(bdd.parsers.parse("the image size should be {size}"))
def ensure_size(size, image):
    expected = geometry(size)
    image_rect = image.sceneRect()
    assert expected.width() == image_rect.width()
    assert expected.height() == image_rect.height()


@bdd.then(bdd.parsers.parse("the image size should not be {size}"))
def ensure_size_not(size, image):
    expected = geometry(size)
    image_rect = image.sceneRect()
    width_neq = expected.width() != image_rect.width()
    height_neq = expected.height() != image_rect.height()
    assert width_neq or height_neq
