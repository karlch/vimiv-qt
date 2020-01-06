# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv.parser import geometry


bdd.scenarios("transform.feature")


@bdd.then(bdd.parsers.parse("the orientation should be {orientation}"))
def ensure_orientation(image, orientation):
    orientation = orientation.lower()
    scenerect = image.scene().sceneRect()
    if orientation == "landscape":
        assert scenerect.width() > scenerect.height()
    elif orientation == "portrait":
        assert scenerect.height() > scenerect.width()
    else:
        raise ValueError(f"Unkown orientation {orientation}")


@bdd.then(bdd.parsers.parse("the image size should be {size}"))
def ensure_size(size, image):
    expected = geometry(size)
    image_rect = image.sceneRect()
    assert expected.width() == image_rect.width()
    assert expected.height() == image_rect.height()
