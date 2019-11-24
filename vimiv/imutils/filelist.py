# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Filelist of images.

The module provides methods to navigate and update the current image filelist. Once a
new image in the filelist is selected, it is passed on to the file handler to open it.
"""

import os
from random import shuffle
from typing import List, Iterable, Optional

from PyQt5.QtCore import QObject, pyqtSlot

from vimiv import api, utils, imutils
from vimiv.commands import search
from vimiv.utils import files, log
from .slideshow import Slideshow


_paths: List[str] = []
_index = 0
_logger = log.module_logger(__name__)


# We want to use the name next here as it is the best name for the command
@api.keybindings.register(["n", "<page-down>"], "next", mode=api.modes.IMAGE)
@api.commands.register()
def next(count: int = 1) -> None:  # pylint: disable=redefined-builtin
    """Select next image.

    **count:** multiplier
    """
    if _paths:
        _set_index((_index + count) % len(_paths))


@api.keybindings.register(["p", "<page-up>"], "prev", mode=api.modes.IMAGE)
@api.commands.register()
def prev(count: int = 1) -> None:
    """Select previous image.

    **count:** multiplier
    """
    if _paths:
        _set_index((_index - count) % len(_paths))


@api.keybindings.register(["G", "<end>"], "goto -1", mode=api.modes.IMAGE)
@api.keybindings.register(["gg", "<home>"], "goto 1", mode=api.modes.IMAGE)
@api.commands.register(mode=api.modes.IMAGE)
def goto(index: int, count: Optional[int] = None) -> None:
    """Select specific image in current filelist.

    **syntax:** ``:goto index``

    positional arguments:
        * ``index``: Number of the image to select.

    .. hint:: -1 is the last image.

    **count:** Select [count]th image instead.
    """
    index = count if count is not None else index
    if index > 0:
        index -= 1
    _set_index(index % len(_paths))


@api.status.module("{abspath}")
def current() -> str:
    """Absolute path to the current image."""
    if _paths:
        return _paths[_index]
    return ""


@api.status.module("{basename}")
def basename() -> str:
    """Basename of the current image."""
    return os.path.basename(current())


@api.status.module("{index}")
def get_index() -> str:  # Needs to be called get as we use index as variable often
    """Index of the current image."""
    if _paths:
        return str(_index + 1).zfill(len(total()))
    return "0"


@api.status.module("{total}")
def total() -> str:
    """Total amount of images."""
    return str(len(_paths))


@api.status.module("{exif-date-time}")
def exif_date_time() -> str:
    """Exif creation date and time of the current image.

    This is meant as an example api.status.module to show how to display exif
    data in the statusbar. If there are any requests/ideas for more, this can
    be used as basis to work with.
    """
    return imutils.exif.exif_date_time(current())


def pathlist() -> List[str]:
    """Return the currently loaded list of paths."""
    return _paths


class SignalHandler(QObject):
    """Class required to interact with Qt signals.

    It updates the filelist when:
        * new search results came in
        * an update from the slideshow is expected
        * the working directory changed.
    """

    @api.objreg.register
    def __init__(self):
        super().__init__()
        search.search.new_search.connect(self._on_new_search)
        # The slideshow object is created here as it is not required by anything else
        # It stays around as it is part of the global object registry
        Slideshow().timeout.connect(self._on_slideshow_event)

        api.signals.load_images.connect(self._on_load_images)
        api.working_directory.handler.images_changed.connect(self._on_images_changed)

    @pyqtSlot(list)
    def _on_load_images(self, paths: List[str]):
        """Load new paths into the filelist.

        This function is used from outside to interact with the filelist. For example by
        the library to update the current selection or by the app to open image paths.
        In case multiple paths are passed, the first element of the list is selected and
        opened, the others are loaded into the list.

        Args:
            paths: List of paths to load into filelist.
        """
        if not paths:
            _logger.debug("Image filelist: no paths to load")
        elif len(paths) == 1:
            _logger.debug("Image filelist: loading single path %s", paths[0])
            _load_single(*paths)
        else:
            _logger.debug("Image filelist: loading %d paths", len(paths))
            _load_paths(paths, paths[0])

    @pyqtSlot(int, list, api.modes.Mode, bool)
    def _on_new_search(
        self, index: int, _matches: List[str], mode: api.modes.Mode, incremental: bool
    ):
        """Select search result after new search.

        Incremental search is ignored for images as highlighting the results is
        not possible anyway and permanently loading images is much too
        expensive.

        Args:
            index: Index to select.
            _matches: List of all matches of the search.
            mode: Mode for which the search was performed.
            incremental: True if incremental search was performed.
        """
        if _paths and not incremental and mode == api.modes.IMAGE:
            _set_index(index)

    @utils.slot
    def _on_slideshow_event(self):
        next(1)
        api.status.update("next image from slideshow event")

    @pyqtSlot(list)
    def _on_images_changed(self, paths: List[str]):
        """React when images were changed by another process."""
        if os.getcwd() != os.path.dirname(current()):  # Images not in filelist
            return
        if paths:  # Some images on disk changed, reload all for safety
            focused_path = current()
            _load_paths(paths, focused_path)
            api.status.update("image filelist changed")
        else:  # No more images in the current filelist
            _clear()


def _set_index(index: int, previous: str = None) -> None:
    """Set the global _index to index."""
    global _index
    _index = index
    if previous != current():
        api.signals.new_image_opened.emit(current())


def _set_paths(paths: List[str]) -> None:
    """Set the global _paths to paths."""
    global _paths
    _paths = paths
    api.signals.new_images_opened.emit(_paths)


def _load_single(path: str) -> None:
    """Populate list of paths in same directory for single path."""
    if path in _paths:
        goto(_paths.index(path) + 1)  # goto is indexed from 1
    else:
        directory = os.path.dirname(path)
        paths, _ = files.supported(files.listdir(directory))
        _load_paths(paths, path)


def _load_paths(paths: Iterable[str], focused_path: str) -> None:
    """Populate imstorage with a new list of paths.

    Args:
        paths: List of paths to load.
        focused_path: The path to display.
    """
    paths = [os.path.abspath(path) for path in paths]
    focused_path = os.path.abspath(focused_path)
    if api.settings.shuffle.value:
        shuffle(paths)
    previous = current()
    _set_paths(paths)
    index = (
        paths.index(focused_path)
        if focused_path in paths
        else min(len(paths) - 1, _index)
    )
    _set_index(index, previous)


def _clear() -> None:
    """Clear all images from the storage as all paths were removed."""
    global _paths, _index
    _paths = []
    _index = 0
    api.signals.all_images_cleared.emit()
