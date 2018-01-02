# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""End2end test: start by opening one image."""

from vimiv import startup
from vimiv.utils import impaths


def test_open_one_image(tmpimage, qtbot, objregistry):
    # Run startup
    startup.run([tmpimage])
    # Assertions
    assert impaths.current() == tmpimage
    assert objregistry.get("image").isVisible()
    assert objregistry.get("statusbar")["right"].text() == "IMAGE"
    assert "foo.png" in objregistry.get("statusbar")["left"].text()
    # TODO More stuff
