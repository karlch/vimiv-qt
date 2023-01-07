# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Mark and tag images."""


import enum
import os
import shutil
from typing import Any, Callable, List, Optional

from PyQt5.QtCore import QObject, pyqtSignal, QFileSystemWatcher, QDateTime

from vimiv.api import commands, keybindings, objreg, status, settings, modes
from vimiv.config import styles
from vimiv.utils import files, xdg, remove_prefix, wrap_style_span, slot, log


_logger = log.module_logger(__name__)


class Mark(QObject):
    """Handle marking and tagging of images.

    Signals:
        marked: Emitted with the image path when an image was marked.
        unmarked: Emitted with the image path when an image was unmarked.
        markdone: Emitted when all image of a given paths list are (un)marked.

    Attributes:
        _indicator: Attribute to cache the evaluated mark indicator string.
        _marked: List of all currently marked images.
        _last_marked: List of images that were marked before clearing.
        _watcher: QFileSystemWatcher to monitor marked paths.
    """

    class Action(enum.Enum):
        """Valid action options for the mark command."""

        Toggle = "toggle"
        Mark = "mark"
        Unmark = "unmark"

    marked = pyqtSignal(str)
    unmarked = pyqtSignal(str)
    markdone = pyqtSignal()

    @objreg.register
    def __init__(self) -> None:
        super().__init__()
        self._indicator: Optional[str] = None
        self._marked: List[str] = []
        self._last_marked: List[str] = []
        self._watcher: Optional[QFileSystemWatcher] = None
        self._actions = {
            Mark.Action.Toggle: self._toggle_mark,
            Mark.Action.Mark: self._mark,
            Mark.Action.Unmark: self._unmark,
        }

    @property
    def tagdir(self) -> str:
        """Path to the tag directory."""
        return Tag.dirname()

    @property
    def watcher(self) -> QFileSystemWatcher:
        """The QFileSystemWatcher to monitor marked paths.

        This is required as during __init__ the QApplication is not created yet.
        """
        if self._watcher is None:
            _logger.debug("Creating watcher to monitor marked paths")
            self._watcher = QFileSystemWatcher()
            self._watcher.fileChanged.connect(self._on_file_changed)
        return self._watcher

    def is_marked(self, path: str) -> bool:
        """Return True if the passed path is marked."""
        return path in self._marked

    @keybindings.register("m", "mark %")
    @commands.register()
    def mark(self, paths: List[str], action: Action = Action.Toggle) -> None:
        """Mark one or more paths.

        **syntax:** ``:mark path [path ...] [--action=ACTION]``

        .. hint:: ``:mark %`` marks the current path.

        positional arguments:
            * ``paths``: The path(s) to mark.

        optional arguments:
            * ``--action``: One of toggle/mark/unmark. Toggle, the default, inverses the
              mark status of the path(s). Mark forces marking while unmark forces
              removing the mark.
        """
        _logger.debug("Calling %s on %d paths", action.value, len(paths))
        function = self._actions[action]
        for path in paths:
            if files.is_image(path):
                try:
                    function(path)
                except ValueError:
                    _logger.debug("Calling %s on '%s' failed", action.value, path)
        self.markdone.emit()

    @commands.register()
    def mark_clear(self) -> None:
        """Clear all marks.

        .. hint::
            It is possible to restore the last cleared marks using ``mark-restore``.
        """
        if not self._marked:
            _logger.debug("No marks to clear")
            return
        _logger.debug("Clearing all marks")
        self.watcher.removePaths(self._marked)
        self._marked, self._last_marked = [], self._marked
        for path in self._last_marked:
            self.unmarked.emit(path)
            _logger.debug("Unmarked '%s'", path)
        self.markdone.emit()

    @commands.register()
    def mark_restore(self) -> None:
        """Restore the last cleared marks."""
        _logger.debug("Restoring last marks")
        self.watcher.addPaths(self._last_marked)
        self._marked, self._last_marked = self._last_marked, []
        for path in self._marked:
            self.marked.emit(path)
            _logger.debug("Marked '%s'", path)
        self.markdone.emit()

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
        _logger.debug("Writing to tag file '%s'", name)
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
        _logger.debug("Deleting tag '%s'", name)
        abspath = Tag.path(name)

        def safe_delete(operation: Callable) -> None:
            """Wrapper around delete operation logging exceptions."""
            try:
                operation(abspath)
            except PermissionError:
                raise commands.CommandError("Permission denied")

        if os.path.isfile(abspath):
            safe_delete(os.remove)
            _logger.debug("Removed regular tag file '%s'", name)
        elif os.path.isdir(abspath):
            safe_delete(shutil.rmtree)
            _logger.debug("Removed tag directory '%s'", name)
        else:
            raise commands.CommandError(f"No tag called '{name}'")

    @commands.register()
    def tag_load(self, name: str) -> None:
        """Load images from a tag into the current mark list.

        **syntax:** ``tag-load name``

        .. hint:: You can open all marked images with ``:open %m``.

        positional arguments:
            * ``name``: Name of the tag to load.
        """
        _logger.debug("Loading tag '%s'", name)
        with Tag(name) as tag:
            paths = tag.read()
        self._marked = paths
        for path in paths:
            self.marked.emit(path)
            _logger.debug("Marked '%s'", path)
        self.markdone.emit()

    @commands.register()
    def tag_open(self, name: str) -> None:
        """Open images from a tag in image mode.

        **syntax:** ``tag-open name``

        .. hint:: This is equivalent to ``:tag-load name && open %m``.

        positional arguments:
            * ``name``: Name of the tag to open.
        """
        from vimiv.api import open_paths  # Otherwise we have a circular import

        self.tag_load(name)
        open_paths(self._marked)

    @status.module("{mark-indicator}")
    def mark_indicator(self) -> str:
        """Indicator if the current image is marked."""
        if modes.current().current_path in self._marked:
            return self.indicator
        return ""

    @status.module("{mark-count}")
    def mark_count(self) -> str:
        """Total number of currently marked images."""
        if self._marked:
            color = styles.get("mark.color")
            return wrap_style_span(f"color: {color}", f"{len(self._marked):02d}")
        return ""

    @property
    def paths(self) -> List[str]:
        """Return list of currently marked paths."""
        return self._marked

    @property
    def indicator(self) -> str:
        """Colored mark indicator."""
        if self._indicator is None:
            color = styles.get("mark.color")
            self._indicator = wrap_style_span(
                f"color: {color}", settings.statusbar.mark_indicator.value
            )
        return self._indicator

    def highlight(self, text: str, marked: bool = True) -> str:
        """Add/remove mark indicator from text.

        If marked is True, then the indicator is added to the left of the text.
        Otherwise it is removed.
        """
        mark_str = self.indicator + " "
        text = remove_prefix(text, mark_str)
        return mark_str + text if marked else text

    def _toggle_mark(self, path: str) -> None:
        """Toggle the mark status of a single path.

        If the path is marked, it is unmarked. Otherwise it is marked.

        Args:
            path: The path to toggle the mark status of.
        """
        _logger.debug("Toggling '%s'", path)
        try:
            self._unmark(path)
        except ValueError:
            self._mark(path)

    @slot
    def _on_file_changed(self, path: str) -> None:
        """Unmark deleted paths."""
        if not os.path.exists(path):
            self._unmark(path)

    def _mark(self, path: str) -> None:
        """Mark the given path."""
        if self.is_marked(path):
            raise ValueError(f"Path '{path}' is already marked")
        self._marked.append(path)
        self.marked.emit(path)
        self.watcher.addPath(path)
        _logger.debug("Marked '%s'", path)

    def _unmark(self, path: str) -> None:
        """Unmark the given path."""
        index = self._marked.index(path)
        del self._marked[index]
        self.unmarked.emit(path)
        self.watcher.removePath(path)
        _logger.debug("Unmarked '%s'", path)


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

        _file: The associated file handler.
        _mode: File mode used for open.
    """

    COMMENTCHAR = "#"

    def __init__(self, name: str, read_only: bool = True):
        self.name = name
        abspath = Tag.path(name)
        exists = os.path.isfile(abspath)
        self._mode = "r" if read_only else ("r+" if exists else "a+")
        _logger.debug("Opened tag object: '%s'", self)
        xdg.makedirs(os.path.dirname(abspath))
        try:
            # We are writing our own context-manager here
            # pylint: disable=consider-using-with
            self._file = open(abspath, self._mode, encoding="utf-8")
        except FileNotFoundError:  # For read-only if the file does not exist
            raise commands.CommandError(f"No tag called '{name}'")
        except OSError as e:
            raise commands.CommandError(f"Error reading '{name}': {e}")

        if read_only:
            _logger.debug("%s: Reading tag file", self)
        elif not exists:
            _logger.debug("%s: Creating new tag file", self)
            self._write_header()
        else:
            _logger.debug("%s: Appending to existing tag file", self)

    def __enter__(self) -> "Tag":
        return self

    def __exit__(self, *_: Any) -> None:
        self._file.close()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.name}, mode={self._mode})"

    def write(self, paths: List[str]) -> None:
        """Write paths to the tag file."""
        existing = {path.strip() for path in self.read()}
        new_paths = set(paths) - existing
        _logger.debug("Adding %d paths to tag file", len(new_paths))
        self._file.write("\n".join(sorted(new_paths)) + "\n")

    def read(self) -> List[str]:
        """Read paths from the tag file."""
        paths = [
            path.strip() for path in self._file if not path.startswith(Tag.COMMENTCHAR)
        ]
        _logger.debug("%s: read %d paths from tag", self, len(paths))
        return paths

    @staticmethod
    def dirname() -> str:
        """Return path to the tag directory."""
        return xdg.vimiv_data_dir("tags")

    @staticmethod
    def path(name: str) -> str:
        """Return absolute path to a tag file called name."""
        return os.path.join(Tag.dirname(), name)

    def _write_header(self) -> None:
        """Write header to a new tag file."""
        self._write_comment("vimiv tag file")
        now = QDateTime.currentDateTime()
        formatted_time = now.toString("yyyy-MM-dd HH:mm")
        self._write_comment(f"created: {formatted_time}")

    def _write_comment(self, comment: str) -> None:
        """Write a comment line to the tag file."""
        self._file.write(f"{Tag.COMMENTCHAR} {comment}\n")
