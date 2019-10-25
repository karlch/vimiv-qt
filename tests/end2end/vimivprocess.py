# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Singleton to start one vimiv process for tests."""

import logging

from PyQt5.QtCore import QThreadPool, QCoreApplication, pyqtBoundSignal, QObject

from vimiv import api, startup
from vimiv.commands import runners
from vimiv.imutils import filelist, immanipulate


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

    def __init__(self, qtbot, argv=None):
        argv = [] if argv is None else argv
        argv.extend(["--temp-basedir"])
        args = startup.setup_pre_app(argv)
        startup.setup_post_app(args)
        # No crazy stuff should happen here, waiting is not really necessary
        api.working_directory.handler.WAIT_TIME = 0.001
        # No key holding happens, waiting is not necessary
        immanipulate.WAIT_TIME = 0.001

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
        api.mark.mark_clear()
        logging.getLogger().handlers = []  # Mainly to remove the statusbar handler
        # Must disconnect these signals ourselves as the automatic disconnection seems
        # to fail with slots assigned using partial or lambdas
        VimivProc.disconnect_custom_signals(api.signals)

    @staticmethod
    def disconnect_custom_signals(obj: QObject):
        """Disconnect all slots from custom signals in obj."""
        for name in dir(obj):
            elem = getattr(obj, name)
            if isinstance(elem, pyqtBoundSignal) and name not in dir(QObject):
                elem.disconnect()