# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Singleton to start one vimiv process for tests."""

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget

# Must mock decorator before import
from unittest import mock
mock.patch("vimiv.utils.misc.cached_method", lambda x: x).start()

from vimiv import startup
from vimiv.utils import objreg
from vimiv.imutils import imstorage


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


class VimivProc():
    """Process class to start and exit one vimiv process."""

    def __init__(self, qtbot, argv=[]):
        argv.append("--temp-basedir")
        startup.run(argv)
        for name, widget in objreg._registry.items():
            if isinstance(widget, QWidget):
                qtbot.addWidget(widget)

    def exit(self):
        # Do not start any new threads
        QThreadPool.globalInstance().clear()
        # Wait for any running threads to exit safely
        QThreadPool.globalInstance().waitForDone()
        objreg.clear()
        imstorage._paths = []
        imstorage._index = 0
