# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to run search."""

import os

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.commands import cmdexc, commands
from vimiv.config import keybindings, settings
from vimiv.gui import statusbar
from vimiv.utils import objreg, pathreceiver


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
            arg3: True if incremental search was performed.
        cleared: Emitted when the search was cleared.
    """

    @objreg.register("search")
    def __init__(self):
        super().__init__()
        self._text = ""
        self._reverse = False

    new_search = pyqtSignal(int, list, bool)
    cleared = pyqtSignal()

    def __call__(self, text, count=1, reverse=False, incremental=False):
        """Run search.

        Args:
            text: The string to search for.
        """
        if not text:
            raise cmdexc.CommandError("no search performed")
        self._text = text
        paths = pathreceiver.pathlist()
        current_index = paths.index(pathreceiver.current())
        basenames = [os.path.basename(path) for path in paths]
        sorted_paths = self._sort_for_search(basenames, current_index, reverse)
        next_match, matches = self._get_next_match(text, count, sorted_paths)
        index = basenames.index(next_match)
        self.new_search.emit(index, matches, incremental)
        statusbar.update()

    @keybindings.add("N", "search-next")
    @commands.register(instance="search", count=1, hide=True)
    def search_next(self, count):
        """Continue search to the next match.

        **syntax:** ``:search-next``

        **count:** multiplier
        """
        self(self._text, count)

    @keybindings.add("P", "search-prev")
    @commands.register(instance="search", count=1, hide=True)
    def search_prev(self, count):
        """Continue search to the previous match.

        **syntax:** ``:search-next``

        **count:** multiplier
        """
        self(self._text, count, True)

    def clear(self):
        """Clear search string."""
        self._text = ""
        self.cleared.emit()

    def _sort_for_search(self, paths, index, reverse):
        """Sort list of paths so the order is usable by search.

        This moves the currently selected image to end of the list and the next
        index to the very front.

        Args:
            paths: List of paths to sort.
            index: The currently selected index.
            reverse: If True sort for reverse search, reversing the list.
        """
        if reverse:
            return paths[index - 1::-1] + paths[-1:index - 1:-1]
        return paths[index + 1:] + paths[:index + 1]

    def _get_next_match(self, text, count, paths):
        """Return the next match from a list of paths.

        Args:
            text: The string to search for.
            count: Defines how many matches to jump forward.
            paths: List of paths to search in.
        """
        matches = [path for path in paths if self._matches(text, path)]
        if matches and count:
            count = count % len(matches)
            return matches[count - 1], matches
        return paths[-1], []

    def _matches(self, first, second):
        """Check if first string is in second string."""
        if settings.get_value(settings.Names.SEARCH_IGNORE_CASE):
            return first.lower() in second.lower()
        return first in second


search = Search()
