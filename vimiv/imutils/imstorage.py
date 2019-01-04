# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Deals with changing and storing paths to currently loaded images."""

import logging
import os
from random import shuffle

from PyQt5.QtCore import pyqtSlot, QObject

from vimiv.commands import commands, search
from vimiv.config import keybindings, settings
from vimiv.gui import statusbar
from vimiv.imutils.imsignals import imsignals
from vimiv.modes import Mode, Modes
from vimiv.utils import objreg, files, slideshow, working_directory


# We need the check as exif support is optional
try:
    import piexif
except ImportError:
    piexif = None


_paths = []
_index = 0


# We want to use the name next here as it is the best name for the command
@keybindings.add("n", "next", mode=Modes.IMAGE)
@commands.register(count=1)
def next(count):  # pylint: disable=redefined-builtin
    """Select next image.

    **count:** multiplier
    """
    if _paths:
        _set_index((_index + count) % len(_paths))


@keybindings.add("p", "prev", mode=Modes.IMAGE)
@commands.register(count=1)
def prev(count):
    """Select previous image.

    **count:** multiplier
    """
    if _paths:
        _set_index((_index - count) % len(_paths))


@keybindings.add("G", "goto -1", mode=Modes.IMAGE)
@keybindings.add("gg", "goto 1", mode=Modes.IMAGE)
@commands.argument("index", type=int)
@commands.register(mode=Modes.IMAGE, count=0)
def goto(index, count):
    """Select specific image in current filelist.

    **syntax:** ``:goto index``

    positional arguments:
        * index: Number of the image to select.

    .. hint:: -1 is the last image.

    **count:** Select [count]th image instead.
    """
    index = count if count else index
    _set_index(index % (len(_paths) + 1) - 1)


@statusbar.module("{abspath}")
def current():
    """Absolute path to the current image."""
    if _paths:
        return _paths[_index]
    return ""


@statusbar.module("{basename}")
def basename():
    """Basename of the current image."""
    return os.path.basename(current())


@statusbar.module("{index}")
def get_index():
    """Index of the current image."""
    if _paths:
        return str(_index + 1).zfill(len(total()))
    return "0"


@statusbar.module("{total}")
def total():
    """Total amount of images."""
    return str(len(_paths))


@statusbar.module("{exif-date-time}")
def exif_date_time():
    """Exif creation date and time of the current image.

    This is meant as an example statusbar module to show how to display exif
    data in the statusbar. If there are any requests/ideas for more, this can
    be used as basis to work with.
    """
    if piexif is not None:
        try:
            exif_dict = piexif.load(current())
            return exif_dict["0th"][piexif.ImageIFD.DateTime].decode()
        except (piexif.InvalidImageDataError, FileNotFoundError, KeyError):
            pass
    return ""


def pathlist():
    """Return the currently loaded list of paths."""
    return _paths


class Storage(QObject):
    """Store and move between paths to images.

    Attributes:
        _paths: List of image paths.
        _index: Index of the currently displayed image in the _paths list.
    """

    @objreg.register
    def __init__(self):
        super().__init__()
        search.search.new_search.connect(self._on_new_search)
        sshow = slideshow.Slideshow()
        sshow.next_im.connect(self._on_slideshow_event)
        imsignals.open_new_image.connect(self._on_open_new_image)
        imsignals.open_new_images.connect(self._on_open_new_images)

        working_directory.handler.images_changed.connect(
            self._on_images_changed)

    @pyqtSlot(int, list, Mode, bool)
    def _on_new_search(self, index, matches, mode, incremental):
        """Select search result after new search.

        Incremental search is ignored for images as highlighting the results is
        not possible anyway and permanently loading images is much too
        expensive.

        Args:
            index: Index to select.
            matches: List of all matches of the search.
            mode: Mode for which the search was performed.
            incremental: True if incremental search was performed.
        """
        if _paths and not incremental and mode == Modes.IMAGE:
            _set_index(index)

    @pyqtSlot()
    def _on_slideshow_event(self):
        next(1)

    @pyqtSlot(str)
    def _on_open_new_image(self, path):
        """Load new image into storage.

        Args:
            path: Path to the new image to load.
        """
        _load_single(os.path.abspath(path))

    @pyqtSlot(list, str)
    def _on_open_new_images(self, paths, focused_path):
        """Load list of new images into storage.

        Args:
            paths: List of paths to the new images to load.
            focused_path: The path to display.
        """
        # Populate list of paths in same directory for single path
        if len(paths) == 1:
            _load_single(focused_path)
        else:
            _load_paths(paths, focused_path)

    @pyqtSlot(list)
    def _on_images_changed(self, paths):
        if os.getcwd() != os.path.dirname(current()):
            return
        if paths:
            focused_path = current()
            _load_paths(paths, focused_path)
            statusbar.update()
        else:
            _clear()
            logging.warning("No more images to display")


def _set_index(index, previous=None):
    """Set the global _index to index."""
    global _index
    _index = index
    if previous != current():
        imsignals.new_image_opened.emit(current())


def _set_paths(paths):
    """Set the global _paths to paths."""
    global _paths
    _paths = paths
    imsignals.new_images_opened.emit(_paths)


def _load_single(path):
    """Populate list of paths in same directory for single path."""
    if path in _paths:
        goto(_paths.index(path) + 1, count=0)  # goto is indexed from 1
    else:
        directory = os.path.dirname(path)
        paths, _ = files.get_supported(files.ls(directory))
        _load_paths(paths, path)


def _load_paths(paths, focused_path):
    """Populate imstorage with a new list of paths.

    Args:
        paths: List of paths to load.
        focused_path: The path to display.
    """
    paths = [os.path.abspath(path) for path in paths]
    focused_path = os.path.abspath(focused_path)
    if settings.get_value(settings.Names.SHUFFLE):
        shuffle(_paths)
    previous = current()
    _set_paths(paths)
    index = paths.index(focused_path) \
        if focused_path in paths \
        else min(len(paths) - 1, _index)
    _set_index(index, previous)


def _clear():
    """Clear all images from the storage as all paths were removed."""
    global _paths, _index
    _paths = []
    _index = 0
    imsignals.all_images_cleared.emit()
