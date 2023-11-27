# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# pylint: disable=missing-module-docstring,wildcard-import,unused-wildcard-import

from vimiv import qt


if qt.USE_PYQT5:
    from PyQt5.QtCore import *
elif qt.USE_PYQT6:
    from PyQt6.QtCore import *
elif qt.USE_PYSIDE6:
    # TODO remove useless-suppression once we add PySide6 back to pylint toxenv
    # pylint: disable=no-name-in-module,undefined-variable,useless-suppression
    from PySide6.QtCore import *
    from PySide6.QtCore import __version__ as PYQT_VERSION_STR

    BoundSignal = SignalInstance
    QT_VERSION_STR = qVersion()

if qt.USE_PYQT:  # Signal aliases
    # pylint: disable=used-before-assignment
    BoundSignal = pyqtBoundSignal
    Signal = pyqtSignal
    Slot = pyqtSlot


class Align:
    """Namespace for easier access to the Qt alignment flags."""

    # pylint: disable=used-before-assignment
    Center = Qt.AlignmentFlag.AlignCenter
    Left = Qt.AlignmentFlag.AlignLeft
    Right = Qt.AlignmentFlag.AlignRight
    Top = Qt.AlignmentFlag.AlignTop
    Bottom = Qt.AlignmentFlag.AlignBottom
