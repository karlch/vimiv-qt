# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Singleton to start one vimiv process for tests."""

from PyQt5.QtCore import QThreadPool, QCoreApplication, pyqtBoundSignal, QObject
from PyQt5.QtWidgets import QWidget

# Must mock decorator before import
from unittest import mock

mock.patch("vimiv.utils.cached_method", lambda x: x).start()

from vimiv import api, startup  # noqa
from vimiv.commands import runners  # noqa
from vimiv.utils import working_directory  # noqa
from vimiv.imutils import filelist  # noqa


_processes = []


def init(qtbot, argv):
    """Create the VimivProc object."""
    assert not _processes, "Not creating another vimiv process"
    _processes.append(VimivProc(qtbot, argv))


def instance():
    """Get the VimivProc object."""
    assert _processes, "No vimiv process created"
    return _processes[0]


def exit():
    """Close the vimiv process."""
    instance().exit()
    del _processes[0]


class VimivProc:
    """Process class to start and exit one vimiv process."""

    def __init__(self, qtbot, argv=[]):
        argv.extend(["--temp-basedir"])
        startup.startup(argv)
        for name, widget in api.objreg._registry.items():
            if isinstance(widget, QWidget):
                qtbot.addWidget(widget)
        # No crazy stuff should happen here, waiting is not really necessary
        working_directory.handler.WAIT_TIME = 0.001

    def exit(self):
        # Do not start any new threads
        QThreadPool.globalInstance().clear()
        # Wait for any running threads to exit safely
        QThreadPool.globalInstance().waitForDone(5000)  # Kill after 5s
        runners._last_command.clear()
        filelist._paths = []
        filelist._index = 0
        # Needed for cleanup
        QCoreApplication.instance().aboutToQuit.emit()
        api.settings.reset()
        # Must disconnect these signals ourselves as the automatic disconnection seems
        # to fail with slots assigned using partial
        for name in dir(api.imutils):
            elem = getattr(api.imutils, name)
            if isinstance(elem, pyqtBoundSignal) and name not in dir(QObject):
                print(name, elem)
                elem.disconnect()
