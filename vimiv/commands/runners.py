# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes to run commands."""

import logging
import shlex
import subprocess

from PyQt5.QtCore import QRunnable, QObject, QThreadPool

from vimiv.commands import commands, cmdexc
from vimiv.gui import statusbar


class CommandRunner():
    """Runner for internal commands."""

    def __call__(self, text, mode):
        """Run internal command when called.

        Splits the given text into count, name and arguments. Then runs the
        command corresponding to name with count and arguments. Emits the
        exited signal when done.

        Args:
            text: String passed as command.
            mode: Mode in which the command is supposed to run.
        """
        count, cmdname, args = self._parse(text)
        try:
            cmd = commands.get(cmdname, mode)
            cmd(args, count=count)
            statusbar.update()
            logging.debug("Ran '%s' succesfully", text)
        except cmdexc.CommandNotFound as e:
            logging.error(str(e))
        except (cmdexc.ArgumentError, cmdexc.CommandError) as e:
            logging.error("%s: %s", cmdname, str(e))
        except cmdexc.CommandWarning as w:
            logging.warning("%s: %s", cmdname, str(w))

    def _parse(self, text):
        """Parse given command text into count, name and arguments.

        Args:
            text: String passed as command.
        Return:
            count: Digits prepending the command to interpret as count.
            name: Name of the command passed.
            args: Arguments passed.
        """
        text = text.strip()
        count = ""
        split = shlex.split(text)
        cmdname = split[0]
        # Receive prepended digits as count
        while cmdname[0].isdigit():
            count += cmdname[0]
            cmdname = cmdname[1:]
        args = split[1:]
        return count, cmdname, args


class ExternalRunner(QObject):
    """Runner for external commands."""

    _pool = QThreadPool.globalInstance()

    def __call__(self, text):
        """Run external command using ShellCommandRunnable.

        Args:
            text: Text parsed as command to run.
        """
        runner = ShellCommandRunnable(text)
        self._pool.start(runner)


class ShellCommandRunnable(QRunnable):
    """Run shell command in an extra thread.

    Captures stdout and stderr. Logging is called according to the returncode
    of the command.

    Attributes:
        _text: Text parsed as command to run.
    """

    def __init__(self, text):
        super().__init__()
        self._text = text

    def run(self):
        try:
            subprocess.run(self._text, shell=True, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            statusbar.update()
            logging.debug("Ran '!%s' succesfully", self._text)
        except subprocess.CalledProcessError as e:
            message = e.stderr.decode().split("\n")[0]
            logging.error("%d  %s", e.returncode, message)
