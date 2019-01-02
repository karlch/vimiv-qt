# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handler to take care of the current working directory."""

import logging
import os

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from vimiv.config import settings


class WorkingDirectoryHandler(QObject):
    """Handler to store and change the current working directory.

    Signals:
        cwd_changed: Emitted when the current working directory has changed.
            arg1: The new working directory.

    Attributes:
        _dir: The current working directory.
        _event_handler: EventHandler object used by _observer to react to
            changes to the directory content.
        _observer: Monitoring observer that emits signals when the directory
            content has changed.
    """

    cwd_changed = pyqtSignal(str)

    # TODO check which of these will be needed
    path_created = pyqtSignal(str)
    path_deleted = pyqtSignal(str)
    path_modified = pyqtSignal(str)
    path_moved = pyqtSignal(str, str)

    dir_created = pyqtSignal(str)
    dir_deleted = pyqtSignal(str)
    dir_modified = pyqtSignal(str)
    dir_moved = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._dir = None
        self._observer = Observer()
        self._event_handler = EventHandler(self)

        settings.signals.changed.connect(self._on_settings_changed)

    def chdir(self, directory):
        """Change the current working directory to directory."""
        directory = os.path.abspath(directory)
        if directory != self._dir:
            self._dir = directory
            os.chdir(directory)
            self._monitor(directory)
            self.cwd_changed.emit(directory)

    def _monitor(self, directory):
        """Monitor directory with watchdog."""
        if not settings.get_value(settings.Names.MONITOR_FS):
            return
        logging.debug("Monitoring %s", directory)
        self._stop_monitoring()
        self._observer = Observer()
        self._observer.schedule(self._event_handler, directory, recursive=False)
        self._observer.start()

    def _stop_monitoring(self):
        self._observer.stop()
        self._observer.unschedule_all()

    @pyqtSlot(str, object)
    def _on_settings_changed(self, setting, new_value):
        if setting == settings.Names.MONITOR_FS:
            if new_value:
                self._monitor(self._dir)
            else:
                logging.debug("Turning monitoring off")
                self._stop_monitoring()


class EventHandler(FileSystemEventHandler):
    """Event handler to emit signals when directory content has changed.

    See: https://pythonhosted.org/watchdog/api.html#event-handler-classes

    Attributes:
        _handler: WorkingDirectoryHandler to use the signals from.
    """

    def __init__(self, wd_handler):
        super().__init__()
        self._handler = wd_handler

    def on_created(self, event):
        logging.debug("Created %s", event.src_path)
        if event.is_directory:
            self._handler.dir_created.emit(event.src_path)
        else:
            self._handler.path_created.emit(event.src_path)

    def on_deleted(self, event):
        logging.debug("Deleted %s", event.src_path)
        if event.is_directory:
            self._handler.dir_deleted.emit(event.src_path)
        else:
            self._handler.path_deleted.emit(event.src_path)

    def on_modified(self, event):
        logging.debug("Modified %s", event.src_path)
        if event.is_directory:
            self._handler.dir_modified.emit(event.src_path)
        else:
            self._handler.path_modified.emit(event.src_path)

    def on_moved(self, event):
        logging.debug("Moved %s to %s", event.src_path, event.dest_path)
        if event.is_directory:
            self._handler.dir_moved.emit(event.src_path, event.dest_path)
        else:
            self._handler.path_moved.emit(event.src_path, event.dest_path)


handler = WorkingDirectoryHandler()
