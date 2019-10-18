# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd


bdd.scenarios("imagezoom.feature")


@bdd.then(bdd.parsers.parse("the zoom level should be {level}"))
def check_zoom_level(image, level):
    im_level = image.current_width() / image.original_width()
    assert float(level) == pytest.approx(im_level, 0.01)


@bdd.then(bdd.parsers.parse("the zoom level should not be {level}"))
def check_zoom_level_not(image, level):
    im_level = image.current_width() / image.original_width()
    assert float(level) != pytest.approx(im_level, 0.01)
