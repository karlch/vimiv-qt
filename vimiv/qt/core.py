# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

# pylint: disable=missing-module-docstring,wildcard-import,unused-wildcard-import

from vimiv import qt


if qt.USE_PYQT5:
    from PyQt5.QtCore import *
elif qt.USE_PYQT6:
    from PyQt6.QtCore import *
elif qt.USE_PYSIDE6:
    # pylint: disable=no-name-in-module,undefined-variable
    from PySide6.QtCore import *
    from PySide6.QtCore import __version__ as PYQT_VERSION_STR

    pyqtSignal = Signal
    pyqtSlot = Slot
    QT_VERSION_STR = qVersion()
