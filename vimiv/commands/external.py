# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Runner for external commands."""

import os
import glob
import shlex
from typing import List

from PyQt5.QtCore import QProcess, QCoreApplication

from vimiv import api
from vimiv.utils import log, flatten, contains_any, escape_glob


_logger = log.module_logger(__name__)


class ExternalRunner:
    """Runner for external commands.

    The runner makes use of the implementation class below which is created on-demand.
    There are two methods to run external commands:
        * The ``run`` function which starts a subprocess of the given command.
        * The ``spawn`` function which starts a shell subprocess with the passed
          arguments.

    Run is preferred in general, as no sub-shell is required, but cannot deal with
    redirection.

    Attributes:
        _impl: The implementation class used to run external commands.
    """

    @api.objreg.register
    def __init__(self):
        self._impl = None

    def __call__(self, *args, **kwargs):
        """Wrapper function to pass arguments to initialized implementation class."""
        if self._impl is None:
            self._impl = _ExternalRunnerImpl()
        return self._impl(*args, **kwargs)

    def run(self, text: str):
        """Run an external command text."""
        text = escape_glob(text.strip())
        pipe = text.endswith("|")
        split = shlex.split(text.rstrip("|"))
        command, args = split[0], split[1:]
        self(command, *args, pipe=pipe)

    @api.commands.register()
    def spawn(self, command: List[str], shell: str = "sh", shellarg: str = "-c"):
        """Spawn a command in a sub-shell.

        **syntax:** ``:spawn command [--shell=shell --shellarg=shellarg]``

        positional arguments:
            * ``command``: Full command with arguments to pass to the shell.

        optional arguments:
            * ``--shell``: The program to use as sub-shell. Default: ``sh``.
            * ``--shellarg``: Argument to prepend for the shell. Default: ``-c``.

        The difference to running commands with ! is that an actual shell is involved
        instead of running the program directly. This means that shell, redirection
        etc. will work in spawn, but not with !. Nevertheless ! is recommended in
        general for performance and security reasons.
        """
        if not command:
            raise api.commands.CommandError("No command to run")
        # Join as the full command is the argument to the shell process
        self(shell, shellarg, " ".join(command))


class _ExternalRunnerImpl(QProcess):
    """Runner for external commands."""

    error_messages = {
        QProcess.FailedToStart: "command not found or not executable",
        QProcess.Crashed: "process crashed after startup",
        QProcess.Timedout: "process timed out",
        QProcess.WriteError: "cannot write to process",
        QProcess.ReadError: "cannot read from process",
        QProcess.UnknownError: "unknown",
    }

    _instance = None

    def __init__(self):
        super().__init__()
        self._pipe = False
        self.finished.connect(self._on_finished)
        self.errorOccurred.connect(self._on_error)
        QCoreApplication.instance().aboutToQuit.connect(self._on_quit)
        _logger.debug("Created implementation of external runner")

    def __call__(self, command: str, *args: str, pipe=False) -> None:
        """Run external command with arguments."""
        if self.state() == QProcess.Running:
            log.warning("Closing running process '%s'", self.program())
            self.close()
        self._pipe = pipe
        arglist: List[str] = flatten(
            glob.glob(arg) if contains_any(arg, "*?[]") else (arg,)  # type: ignore
            for arg in args
        )
        _logger.debug("Running external command '%s' with '%r'", command, arglist)
        self.start(command, arglist)

    def _on_finished(self, exitcode, exitstatus):
        """Check exit status and possibly process standard output on completion."""
        if exitstatus != QProcess.NormalExit or exitcode != 0:
            log.error(
                "Error running external process '%s':\n%s",
                self.program(),
                str(self.readAllStandardError(), "utf-8").strip(),
            )
        elif self._pipe:
            self._process_pipe()
        else:
            _logger.debug("Finished external process '%s' succesfully", self.program())

    def _process_pipe(self) -> None:
        """Open paths from stdout."""
        _logger.debug("Opening paths from '%s'...", self.program())
        stdout = str(self.readAllStandardOutput(), "utf-8")  # type: ignore
        try:
            api.open(path for path in stdout.split("\n") if os.path.exists(path))
            _logger.debug("... opened paths from pipe")
            api.status.update("opened paths from pipe")
        except api.commands.CommandError:
            log.warning("%s: No paths from pipe", self.program())

    def _on_error(self, error):
        log.error("Error running '%s': %s", self.program(), self.error_messages[error])

    def _on_quit(self):
        if self.state() == QProcess.Running:
            log.warning(
                "Decoupling external command '%s' with pid %d",
                self.program(),
                self.pid(),
            )
