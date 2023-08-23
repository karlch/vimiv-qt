# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Helper module to synchronize selection of library and thumbnail mode.

Module Attributes:
    signals: Signals used as synchronization method.
"""


from vimiv.qt.core import Signal, QObject


class _Signals(QObject):
    new_library_path_selected = Signal(str)
    new_thumbnail_path_selected = Signal(str)


signals = _Signals()
