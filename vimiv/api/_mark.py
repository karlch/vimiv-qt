# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Mark and tag images."""

from typing import List

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.utils import files, pathreceiver
from . import commands, keybindings, objreg, status


class Mark(QObject):
    """Handle marking and tagging of images.

    Signals:
        marked: Emitted with the image path when an image was marked.
        unmarked: Emitted with the image path when an image was unmarked.

    Attributes:
        _marked: List of all currently marked images.
        _last_marked: List of images that were marked before clearing.
    """

    marked = pyqtSignal(str)
    unmarked = pyqtSignal(str)

    @objreg.register
    def __init__(self) -> None:
        super().__init__()
        self._marked: List[str] = []
        self._last_marked: List[str] = []

    @keybindings.register("m", "mark %")
    @commands.register()
    def mark(self, paths: List[str]) -> None:
        """Mark one or more paths.

        **syntax:** ``:mark path [path ...]``

        If a path is currently marked, it is unmarked instead.

        positional arguments:
            * ``paths``: The path(s) to mark.
        """
        for path in (path for path in paths if files.is_image(path)):
            self._toggle_mark(path)

    @commands.register()
    def mark_clear(self) -> None:
        """Clear all marks.

        .. hint::
            It is possible to restore the last cleared marks using ``mark-restore``.
        """
        self._marked, self._last_marked = [], self._marked
        for path in self._last_marked:
            self.unmarked.emit(path)

    @commands.register()
    def mark_restore(self) -> None:
        """Restore the last cleared marks."""
        self._marked, self._last_marked = self._last_marked, []
        for path in self._marked:
            self.marked.emit(path)

    @status.module("{mark-indicator}")
    def mark_indicator(self) -> str:
        """Indicator if the current image is marked."""
        if pathreceiver.current() in self._marked:
            return "*"
        return ""

    @status.module("{mark-count}")
    def mark_count(self) -> str:
        """Total number of currently marked images."""
        if self._marked:
            return f"({len(self._marked):d} marked)"
        return ""

    def _toggle_mark(self, path: str) -> None:
        """Toggle the mark status of a single path.

        If the path is marked, it is unmarked. Otherwise it is marked.

        Args:
            path: The path to toggle the mark status of.
        """
        try:
            index = self._marked.index(path)
            del self._marked[index]
            self.unmarked.emit(path)
        except ValueError:
            self._marked.append(path)
            self.marked.emit(path)
