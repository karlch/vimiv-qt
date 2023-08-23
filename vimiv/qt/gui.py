# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# pylint: disable=missing-module-docstring,wildcard-import,unused-wildcard-import

from vimiv import qt


if qt.USE_PYQT5:
    from PyQt5.QtGui import *
elif qt.USE_PYQT6:
    from PyQt6.QtGui import *
elif qt.USE_PYSIDE6:
    from PySide6.QtGui import *
