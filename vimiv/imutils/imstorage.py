# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Deals with changing and storing paths to currently loaded images."""

import os
from random import shuffle

from PyQt5.QtCore import pyqtSlot, QObject

from vimiv import app
from vimiv.commands import commands, search
from vimiv.config import keybindings, settings
from vimiv.gui import statusbar
from vimiv.imutils.imsignals import imsignals
from vimiv.modes import Modes
from vimiv.utils import objreg, files, slideshow, trash_manager


# We need the check as exif support is optional
try:
    import piexif
except ImportError:
    piexif = None


_paths = []
_index = 0


@keybindings.add("n", "next", mode=Modes.IMAGE)
@commands.register(count=1)
def next(count):
    """Select next image.

    **count:** multiplier
    """
    if _paths:
        _set_index((_index + count) % len(_paths))
        imsignals.path_loaded.emit(current())


@keybindings.add("p", "prev", mode=Modes.IMAGE)
@commands.register(count=1)
def prev(count):
    """Select previous image.

    **count:** multiplier
    """
    if _paths:
        _set_index((_index - count) % len(_paths))
        imsignals.path_loaded.emit(current())


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
    imsignals.path_loaded.emit(current())


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
        trash_manager.signals.path_removed.connect(self._on_path_removed)
        trash_manager.signals.path_restored.connect(self._on_path_restored)
        imsignals.update_index.connect(self._on_update_index)
        imsignals.update_path.connect(self._on_update_path)
        imsignals.update_paths.connect(self._on_update_paths)

    @pyqtSlot(int, list, str, bool)
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
        if _paths and not incremental and mode == "image":
            _set_index(index)
            imsignals.path_loaded.emit(current())

    @pyqtSlot()
    def _on_slideshow_event(self):
        next(1)

    @pyqtSlot(int)
    def _on_update_index(self, index):
        goto(index, 0)

    @pyqtSlot(str)
    def _on_update_path(self, path):
        if path in _paths:
            goto(_paths.index(path) + 1, 0)
        else:
            _load_single(path)

    @pyqtSlot(list, int)
    def _on_update_paths(self, paths, index):
        """Load new paths into storage.

        Args:
            paths: List of paths to load.
            index: Index of the path to display.
        """
        paths = [os.path.abspath(path) for path in paths]
        directory = os.path.dirname(paths[0])
        imsignals.maybe_update_library.emit(directory)
        # Populate list of paths in same directory for single path
        if len(paths) == 1:
            _load_single(paths[0])
        else:
            _set_index(index)
            _set_paths(paths)
            if settings.get_value(settings.Names.SHUFFLE):
                shuffle(_paths)
            imsignals.paths_loaded.emit(_paths)
            imsignals.path_loaded.emit(current())

    @pyqtSlot(str)
    def _on_path_removed(self, path):
        """Remove path from filelist and reload paths if necessary."""
        if path in _paths:
            path_index = _paths.index(path)
            current_path = current()
            _paths.remove(path)
            # Select parent directory in library if no more paths are available
            if not _paths:
                # TODO clear the image displayed
                app.open("..")
            # Move to next image available if the current path was removed
            elif path == current_path:
                _set_index(min(path_index, len(_paths) - 1))
                imsignals.path_loaded.emit(current())
            # Make sure the current image is still selected
            else:
                _set_index(_paths.index(current_path))

    @pyqtSlot(str)
    def _on_path_restored(self, path):
        """Restore path to filelist and reload paths if necessary."""
        if files.is_image(path) and \
                os.path.dirname(path) == os.path.dirname(current()):
            current_path = current()
            _paths.append(path)
            _paths.sort()
            _set_index(_paths.index(current_path))


def _set_index(index):
    """Set the global _index to index."""
    try:
        imsignals.maybe_write_file.emit(current())
    except IndexError:  # Image has been deleted
        pass
    global _index
    _index = index


def _set_paths(paths):
    """Set the global _paths to paths."""
    global _paths
    _paths = paths


def _load_single(path):
    """Populate list of paths in same directory for single path."""
    directory = os.path.dirname(path)
    paths, _ = files.get_supported(files.ls(directory))
    if settings.get_value(settings.Names.SHUFFLE):
        shuffle(paths)
    _set_index(paths.index(path))
    _set_paths(paths)  # Must update after index for maybe_write
    imsignals.paths_loaded.emit(_paths)
    imsignals.path_loaded.emit(current())
