# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Search class implementing functions to search.

Module Attributes:
    search: Instance of the Search class used.
"""

import fnmatch
import os

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv import api


def use_incremental(mode):
    """Return True if incremental search should be used.

    Args:
        mode: Mode for which search should be run.
    """
    enabled = api.settings.search.incremental.value
    if enabled and mode in (api.modes.LIBRARY, api.modes.THUMBNAIL):
        return True
    return False


class Search(QObject):
    """Command runner for searching.

    The class retrieves a list of paths and searches for a given string in the
    paths. When results are found, the new_search signal is emitted with the
    index to select and a list of search results.

    Attributes:
        _text: The string to search for.
        _reverse: Search in reverse mode.

    Signals:
        new_search: Emitted when a new search result is found.
            arg1: Integer of the index to select.
            arg2: List of all search results.
            arg3: Mode for which the search was performed.
            arg4: True if incremental search was performed.
        cleared: Emitted when the search was cleared.
    """

    new_search = pyqtSignal(int, list, api.modes.Mode, bool)
    cleared = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._text = ""
        self._reverse = False

    def __call__(
        self, text, mode, count=0, reverse=False, incremental=False
    ):  # pylint: disable=count-default-zero
        """Run search.

        This method is called from the command line and stores text and reverse
        for the search-next and search-prev commands.

        Args:
            text: The string to search for.
        """
        self._text = text
        self._reverse = reverse
        self._run(text, mode, count, reverse, incremental)

    def repeat(self, count, reverse=False):
        """Repeat last search.

        Used by the search-next and search-prev commands.
        """
        reverse = reverse if not self._reverse else not reverse
        mode = api.modes.current()
        if not self._text:
            raise api.commands.CommandError("No search performed")
        self._run(self._text, mode, count, reverse, False)

    def _run(self, text, mode, count, reverse, incremental):
        """Implementation of running search."""
        paths = api.pathlist(mode)
        current_index = paths.index(api.current_path(mode))
        basenames = [os.path.basename(path) for path in paths]
        sorted_paths = _sort_for_search(basenames, current_index, reverse)
        next_match, matches = _get_next_match(text, count, sorted_paths)
        index = basenames.index(next_match)
        self.new_search.emit(index, matches, mode, incremental)
        api.status.update("new search")

    def clear(self):
        """Clear search string."""
        self._text = ""
        self._reverse = False
        self.cleared.emit()

    def connect_signals(self):
        """Connect working directory handler related signals.

        This allows search to react appropriately when the working directory was changed
        or a new directory was loaded. Cannot be done in the constructor, as the handler
        is not initialized by then.
        """
        api.working_directory.handler.loaded.connect(self.clear)
        api.working_directory.handler.changed.connect(self._on_directory_changed)

    def _on_directory_changed(self, _images, _directories):
        """Re-run search, when the working directory changed."""
        if self._text:
            self(self._text, api.modes.current())


search = Search()


@api.keybindings.register("N", "search-next")
@api.commands.register(hide=True)
def search_next(count: int = 1):
    """Continue search to the next match.

    **syntax:** ``:search-next``

    **count:** multiplier
    """
    search.repeat(count)


@api.keybindings.register("P", "search-prev")
@api.commands.register(hide=True)
def search_prev(count: int = 1):
    """Continue search to the previous match.

    **syntax:** ``:search-next``

    **count:** multiplier
    """
    search.repeat(count, reverse=True)


def _sort_for_search(paths, index, reverse):
    """Sort list of paths so the order is usable by search.

    This moves the currently selected image to end of the list and the next
    index to the very front.

    Args:
        paths: List of paths to sort.
        index: The currently selected index.
        reverse: If True sort for reverse search, reversing the list.
    """
    if reverse:
        return paths[index::-1] + paths[-1:index:-1]
    return paths[index:] + paths[:index]


def _get_next_match(text, count, paths):
    """Return the next match from a list of paths.

    Args:
        text: The string to search for.
        count: Defines how many matches to jump forward.
        paths: List of paths to search in.
    """
    matches = [path for path in paths if _matches(path, text)]
    if matches:
        count = count % len(matches)
        return matches[count], matches
    return paths[0], []


def _matches(path, pattern):
    """Return True if path matches pattern.

    This uses fnmatch to perform unix-style filename pattern matching.
    """
    if api.settings.search.ignore_case.value:
        return fnmatch.fnmatchcase(path.lower(), f"*{pattern.lower()}*")
    return fnmatch.fnmatchcase(path, f"*{pattern}*")
