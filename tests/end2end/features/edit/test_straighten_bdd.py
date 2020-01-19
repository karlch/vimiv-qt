# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

from PyQt5.QtCore import Qt

import pytest
import pytest_bdd as bdd

import vimiv.gui.straighten_widget


bdd.scenarios("straighten.feature")


def find_straighten_widgets(image):
    return image.findChildren(vimiv.gui.straighten_widget.StraightenWidget)


@pytest.fixture()
def straighten(image):
    """Fixture to retrieve the current instance of the straighten widget."""
    widgets = find_straighten_widgets(image)
    assert len(widgets) == 1, "Wrong number of straighten wigets found"
    return widgets[0]


@bdd.when(bdd.parsers.parse("I straighten by {angle:g} degrees"))
@bdd.when(bdd.parsers.parse("I straighten by {angle:g} degree"))
def straighten_by(qtbot, straighten, angle):
    def check():
        assert straighten.transform.angle == pytest.approx(angle)

    straighten.rotate(angle=angle)
    qtbot.waitUntil(check)


@bdd.when(bdd.parsers.parse("I leave the straighten widget via {keyname}"))
def leave_straighten_via_key(qtbot, straighten, keyname):
    keyname = keyname.lower()
    keys = {"<escape>": Qt.Key_Escape, "<return>": Qt.Key_Return}
    try:
        key = keys[keyname]
    except KeyError:
        raise KeyError(f"Must leave straighten widget with one of: {', '.join(keys)}")
    qtbot.keyClick(straighten, key)


@bdd.when(bdd.parsers.parse("I hit {keys} on the straighten widget"))
def press_key_straighten(qtbot, straighten, keys):
    qtbot.keyClick(straighten, keys)


@bdd.then(bdd.parsers.parse("there should be {number:d} straighten widgets"))
@bdd.then(bdd.parsers.parse("there should be {number:d} straighten widget"))
def check_number_of_straighten_widgets(qtbot, image, number):
    def check():
        assert len(find_straighten_widgets(image)) == number

    qtbot.waitUntil(check)


@bdd.then(bdd.parsers.parse("the straighten angle should be {angle:.f}"))
def check_straighten_angle(qtbot, straighten, angle):
    def check():
        assert straighten.angle == pytest.approx(angle)

    qtbot.waitUntil(check)
