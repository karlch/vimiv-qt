# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Class to handle communication between image and utilities."""

from PyQt5.QtCore import QObject, pyqtSignal


class ImageCommunicate(QObject):
    """Class with signals to communicate between image and utilities.

    Signals:
        image_loaded: Emitted with the path when a new image was loaded.
        paths_loaded: Emitted with the list of paths when new paths were
            loaded.
        update_index: Emitted with the index when the image should select a new
            index.
        update_path: Emitted with the path when the image should select a new
            path.
        load_paths: Emitted with the list of paths when new paths should be
            loaded.
    """

    image_loaded = pyqtSignal(str)
    paths_loaded = pyqtSignal(list)
    update_index = pyqtSignal(int)
    update_path = pyqtSignal(str)
    load_paths = pyqtSignal(list)


signals = ImageCommunicate()
