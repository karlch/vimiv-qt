# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
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
