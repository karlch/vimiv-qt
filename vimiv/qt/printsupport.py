# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

# pylint: disable=missing-module-docstring,wildcard-import,unused-wildcard-import

from vimiv import qt
from vimiv.qt import gui


if qt.USE_PYQT5:
    from PyQt5.QtPrintSupport import *

    Orientation = QPrinter.Orientation
elif qt.USE_PYQT6:
    from PyQt6.QtPrintSupport import *

    Orientation = gui.QPageLayout.Orientation
elif qt.USE_PYSIDE6:
    from PySide6.QtPrintSupport import *

    Orientation = gui.QPageLayout.Orientation