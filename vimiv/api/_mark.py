# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Mark and tag images."""


import logging
import os
import shutil
from datetime import datetime
from typing import Any, Callable, List

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.config import styles
from vimiv.utils import files, pathreceiver, xdg, remove_prefix
from . import commands, keybindings, objreg, status, settings


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

        .. hint:: ``:mark %`` marks the current path.

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

    @commands.register()
    def tag_write(self, name: str) -> None:
        """Write marked paths to a tag.

        **syntax:** ``:tag-write name``

        This writes all currently marked images to this tag. This allows storing a
        selection of marked images under a name and re-loading them in later sessions
        using ``:tag-load name``. If the tag file exists, all marked paths that are not
        in the tag are appended to it.

        .. hint::
            It is possible to group tags into directories by dividing the name into a
            directory tree, e.g. ``:tag-write favourites/2017``.

        positional arguments:
            * ``name``: Name of the tag to create.
        """
        with Tag(name, read_only=False) as tag:
            tag.write(self.paths)

    @commands.register()
    def tag_delete(self, name: str) -> None:
        """Delete an existing tag.

        **syntax:** ``:tag-delete name``

        .. warning:: If you pass a tag group directory, the complete tree is deleted.

        positional arguments:
            * ``name``: Name of the tag to delete.
        """
        abspath = Tag.path(name)

        def safe_delete(operation: Callable) -> None:
            """Wrapper around delete operation logging exceptions."""
            try:
                operation(abspath)
            except PermissionError:
                raise commands.CommandError(f"permission denied")

        if os.path.isfile(abspath):
            safe_delete(os.remove)
        elif os.path.isdir(abspath):
            safe_delete(shutil.rmtree)
        else:
            raise commands.CommandError(f"tag file '{name}' does not exist")

    @commands.register()
    def tag_load(self, name: str) -> None:
        """Load images from a tag into the current mark list.

        **syntax:** ``tag-load name``

        .. hint:: You can open all marked images with ``:open %m``.

        positional arguments:
            * ``name``: Name of the tag to delete.
        """
        with Tag(name) as tag:
            paths = tag.read()
        self._marked = paths
        for path in paths:
            self.marked.emit(path)

    @status.module("{mark-indicator}")
    def mark_indicator(self) -> str:
        """Indicator if the current image is marked."""
        if pathreceiver.current() in self._marked:
            return Mark.indicator()
        return ""

    @status.module("{mark-count}")
    def mark_count(self) -> str:
        """Total number of currently marked images."""
        if self._marked:
            return f"({len(self._marked):d} marked)"
        return ""

    @property
    def paths(self) -> List[str]:
        """Return list of currently marked paths."""
        return self._marked

    @staticmethod
    def indicator() -> str:
        """Colored mark indicator."""
        color = styles.get("mark.color")
        return (
            f"<span style='color: {color};'>"
            f"{settings.statusbar.mark_indicator.value}"
            "</span>"
        )

    @staticmethod
    def highlight(text: str, marked: bool = True) -> str:
        """Add/remove mark indicator from text.

        If marked is True, then the indicator is added to the left of the text.
        Otherwise it is removed.
        """
        mark_str = Mark.indicator() + " "
        text = remove_prefix(text, mark_str)
        return mark_str + text if marked else text

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


class Tag:
    """Contextmanager to work with tag files.

    Usage:
        >>> # For reading
        >>> with Tag("name", read_only=True) as tag:
        >>>    paths = tag.read()

        >>> # For writing
        >>> with Tag("name", read_only=False) as tag:
        >>>    tag.write(["path1", "path2", ...])

    Class attributes:
        COMMENTCHAR: Character prepended to comment lines.

    Attributes:
        name: Name of the tag file.
        mode: File mode used for open.

        _file: The associated file handler.
    """

    COMMENTCHAR = "#"

    def __init__(self, name: str, read_only: bool = True):
        self.name = name
        abspath = Tag.path(name)
        exists = os.path.isfile(abspath)
        self.mode = "r" if read_only else ("r+" if exists else "a+")
        logging.debug("Opened tag object: %s", self)
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        self._file = open(abspath, self.mode)

        if read_only:
            logging.debug("%s: Reading tag file", self)
        elif not exists:
            logging.debug("%s: Creating new tag file", self)
            self._write_header()
        else:
            logging.debug("%s: Appending to existing tag file", self)

    def __enter__(self) -> "Tag":
        return self

    def __exit__(self, *_: Any) -> None:
        self._file.close()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.name}, mode={self.mode})"

    def write(self, paths: List[str]) -> None:
        """Write paths to the tag file."""
        existing = {path.strip() for path in self.read()}
        new_paths = set(paths) - existing
        self._file.write("\n".join(sorted(new_paths)) + "\n")

    def read(self) -> List[str]:
        """Read paths from the tag file."""
        paths = [
            path.strip() for path in self._file if not path.startswith(Tag.COMMENTCHAR)
        ]
        logging.debug("%s: read %d paths from tag", self, len(paths))
        return paths

    @staticmethod
    def dirname() -> str:
        """Return path to the tag directory."""
        return xdg.join_vimiv_data("tags")

    @staticmethod
    def path(name: str) -> str:
        """Return absolute path to a tag file called name."""
        return os.path.join(Tag.dirname(), name)

    def _write_header(self) -> None:
        """Write header to a new tag file."""
        self._write_comment("vimiv tag file")
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M")
        self._write_comment(f"created: {formatted_time}")

    def _write_comment(self, comment: str) -> None:
        """Write a comment line to the tag file."""
        self._file.write(f"{Tag.COMMENTCHAR} {comment}\n")
