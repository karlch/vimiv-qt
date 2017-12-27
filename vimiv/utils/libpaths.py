# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Deals with storing paths for the library."""

import os

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.config import settings
from vimiv.utils import files, htmltags


class Signals(QObject):
    """Class to store the qt signals for the library to connect to."""

    loaded = pyqtSignal(list)


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
    data = []
    _extend_data(data, directories, dirs=True)
    _extend_data(data, images)
    os.chdir(directory)
    signals.loaded.emit(data)


def _extend_data(data, paths, dirs=False):
    """Extend list with list of data tuples for paths.

    Generates a tuple in the form of (name, size) for each path and adds it to
    the data list.

    Args:
        data: List to extend.
        paths: List of paths to generate data for.
        dirs: Whether all paths are directories.
    """
    if not paths:
        return data
    for path in paths:
        name = os.path.basename(path)
        if dirs:
            name = htmltags.add("b", name + "/")
        size = files.get_size(path)
        data.append((name, size))
