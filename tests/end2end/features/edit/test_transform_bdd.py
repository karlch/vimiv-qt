# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2022 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd


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
