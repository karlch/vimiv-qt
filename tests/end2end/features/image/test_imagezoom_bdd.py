# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv.gui import image


bdd.scenarios("imagezoom.feature")


@bdd.then(bdd.parsers.parse("the zoom level should be {level}"))
def check_zoom_level(level):
    img = image.instance()
    im_level = img.pixmap().width() / img.original().width()
    assert float(level) == pytest.approx(im_level, 0.01)
