# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

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
