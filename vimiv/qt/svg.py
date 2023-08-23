# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# pylint: disable=missing-module-docstring

from vimiv import qt
from vimiv.utils import lazy

# Lazy import the module that implements QSvgWidget
if qt.USE_PYQT5:
    QtSvg = lazy.import_module("PyQt5.QtSvg", optional=True)
elif qt.USE_PYQT6:
    QtSvg = lazy.import_module("PyQt6.QtSvgWidgets", optional=True)
elif qt.USE_PYSIDE6:
    QtSvg = lazy.import_module("PySide6.QtSvgWidgets", optional=True)
