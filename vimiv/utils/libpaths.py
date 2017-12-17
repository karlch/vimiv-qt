# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Deals with storing paths for the library."""

import os

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.config import settings
from vimiv.utils import files


class Signals(QObject):
    """Class to store the qt signals for the library to connect to."""

    loaded = pyqtSignal(list, list)


signals = Signals()


def load(directory):
    """Load paths in one directory for the library.

    Gets all supported files in the directory and emits the loaded signal.

    Args:
        directory: The directory to load.
    """
    paths = files.ls(directory,
                     show_hidden=settings.get_value("library.show_hidden"))
    images, directories = files.get_supported(paths)
    os.chdir(directory)
    signals.loaded.emit(images, directories)
