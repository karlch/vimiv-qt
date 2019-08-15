# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Utilities to load, edit, navigate and save images`.

The Image Loading Process
,,,,,,,,,,,,,,,,,,,,,,,,,

The image loading process is started by emitting the ``load_images`` signal. It is for
example emitted by the library when a new image path was selected, in thumbnail mode
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

To open an image the ``new_image_opened`` signal is emitted with the absolute path to
this image. This signal is accepted by the file handler in
``vimiv.imutils._file_handler`` which then loads the actual image from disk using
``QImageReader``. Once the format of the image has been determined, and a displayable Qt
widget has been created, the file handler emits one of:

* ``pixmap_loaded`` for standard images
* ``movie_loaded`` for animated Gifs
* ``svg_loaded`` for vector graphics

The image widget in ``vimiv.gui.image`` connects to these signals and displays
the appropriate Qt widget.
"""

from . import exif
from .filelist import current, pathlist
from .filelist import SignalHandler as _FilelistSignalHandler
from ._file_handler import ImageFileHandler as _ImageFileHandler


def init():
    """Initialize the classes needed for imutils."""
    _FilelistSignalHandler()
    _ImageFileHandler()
