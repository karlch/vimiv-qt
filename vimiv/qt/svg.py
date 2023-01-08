# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

# pylint: disable=missing-module-docstring,wildcard-import,unused-wildcard-import

from vimiv import qt
from vimiv.utils import lazy

# Lazy import the module that implements QSvgWidget
if qt.USE_PYQT5:
    QtSvg = lazy.import_module("PyQt5.QtSvg", optional=True)
elif qt.USE_PYQT6:
    QtSvg = lazy.import_module("PyQt6.QtSvgWidgets", optional=True)
elif qt.USE_PYSIDE6:
    QtSvg = lazy.import_module("PySide6.QtSvgWidgets", optional=True)
