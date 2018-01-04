# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv.config import settings
from vimiv.utils import objreg


bdd.scenarios("libraryresize.feature")


@bdd.then(bdd.parsers.parse("the library width should be {fraction}"))
def check_library_size(fraction, qtbot):
    fraction = float(fraction)
    # Check if setting was updated
    assert settings.get_value("library.width") == pytest.approx(fraction)
    # Check if width fits fraction of main window
    library = objreg.get("library")
    mw = objreg.get("mainwindow")
    assert library.width() / mw.width() == float(fraction)
