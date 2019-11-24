# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Helper module to synchronize selection of library and thumbnail mode.

Module Attributes:
    signals: Signals used as synchronization method.
"""


from PyQt5.QtCore import pyqtSignal, QObject


class _Signals(QObject):
    new_library_path_selected = pyqtSignal(str)
    new_thumbnail_path_selected = pyqtSignal(str)


signals = _Signals()
