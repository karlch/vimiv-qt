# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Utilities to load, edit, navigate and save images`.

The image loading process:
    The image loading process is started by calling the :func:`load` function. It is for
    example called by the library when a new image path was selected, in thumbnail mode
    upon selection or by the ``:open`` command. There are a few different cases that are
    taken care of:

    * Loading a single path that is already in the filelist
        In this case the filelist navigates to the appropriate index and the image is
        opened.
    * Loading a single path that is not in the filelist
        The filelist is populated with all images in the same directory as this path and
        the path is opened.
    * Loading multiple paths
        The filelist is populated with these paths and the first file in the list is
        opened.

    To open an image the ``new_image_opened`` signal is emitted with the absolute path
    to this image. This signal is accepted by the file handler in
    ``vimiv.imutils._file_handler`` which then loads the actual image from disk using
    ``QImageReader``. Once the format of the image has been determined, and a
    displayable Qt widget has been created, the file handler emits one of:

    * ``pixmap_loaded`` for standard images
    * ``movie_loaded`` for animated Gifs
    * ``svg_loaded`` for vector graphics

    The image widget in ``vimiv.gui.image`` connects to these signals and displays
    the appropriate Qt widget.

Image editing modules:
    .. automodule:: vimiv.imutils.imtransform

    .. automodule:: vimiv.imutils.immanipulate
       :members: ManipulationGroup
       :private-members:
"""

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie

from . import exif
from .filelist import load, current, pathlist
from .filelist import SignalHandler as _FilelistSignalHandler
from ._file_handler import ImageFileHandler as _ImageFileHandler


def init():
    """Initialize the classes needed for imutils."""
    _FilelistSignalHandler()
    _ImageFileHandler()


class _ImageSignalHandler(QObject):
    """Qt signal handler class for the image related signals.

    Signals:
        new_image_opened: Emitted when the filelist loaded a new path.
            arg1: Path of the new image.
        new_images_opened: Emitted when the filelist loaded new paths.
            arg1: List of new paths.
        all_images_cleared: Emitted when there are no more paths in the filelist.

        image_changed: Emitted when the current image changed on disk.

        pixmap_loaded: Emitted when the file handler loaded a new pixmap.
            arg1: The QPixmap loaded.
            arg2: True if it is only reloaded.
        movie_loaded: Emitted when the file handler loaded a new animation.
            arg1: The QMovie loaded.
            arg2: True if it is only reloaded.
        svg_loaded: Emitted when the file handler loaded a new vector graphic.
            arg1: The path as the VectorGraphic class is constructed directly.
            arg2: True if it is only reloaded.
    """

    # Emited when new image path(s) were opened
    new_image_opened = pyqtSignal(str)
    new_images_opened = pyqtSignal(list)
    all_images_cleared = pyqtSignal()

    # Emitted when the current image changed on disk
    image_changed = pyqtSignal()

    # Tell the image to get a new object to display
    pixmap_loaded = pyqtSignal(QPixmap, bool)
    movie_loaded = pyqtSignal(QMovie, bool)
    svg_loaded = pyqtSignal(str, bool)


_signal_handler = _ImageSignalHandler()  # Instance of Qt signal handler to work with


# Convenience access to the signals
new_image_opened = _signal_handler.new_image_opened
new_images_opened = _signal_handler.new_images_opened
all_images_cleared = _signal_handler.all_images_cleared
image_changed = _signal_handler.image_changed
pixmap_loaded = _signal_handler.pixmap_loaded
movie_loaded = _signal_handler.movie_loaded
svg_loaded = _signal_handler.svg_loaded
