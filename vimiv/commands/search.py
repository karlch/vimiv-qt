# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to run search."""

import os

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.commands import commands
from vimiv.config import keybindings, settings
from vimiv.gui import statusbar
from vimiv.utils import objreg, pathreceiver


class Search(QObject):

    @objreg.register("search")
    def __init__(self):
        super().__init__()
        self._text = ""
        self._reverse = False

    new_search = pyqtSignal(int, list)

    def __call__(self, text, count=1, reverse=False):
        """Run search.

        Args:
            text: The string to search for.
        """
        self._text = text
        paths = pathreceiver.pathlist()
        current_index = paths.index(pathreceiver.current())
        basenames = [os.path.basename(path) for path in paths]
        sorted_paths = self._sort_for_search(basenames, current_index, reverse)
        next_match, matches = self._get_next_match(text, count, sorted_paths)
        index = basenames.index(next_match)
        self.new_search.emit(index, matches)
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

    def _sort_for_search(self, paths, index, reverse):
        if reverse:
            return paths[index - 1::-1] + paths[-1:index - 1:-1]
        return paths[index + 1:] + paths[:index + 1]

    def _get_next_match(self, text, count, paths):
        matches = [path for path in paths if self._matches(text, path)]
        if matches and count:
            count = count % len(matches)
            return matches[count - 1], matches
        return paths[-1], []

    def _matches(self, first, second):
        """Check if first string is in second string."""
        if settings.get_value("search.ignore_case"):
            return first.lower() in second.lower()
        return first in second
