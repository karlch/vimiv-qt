# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import abc
import shlex

from PyQt5.QtCore import pyqtSignal, QObject

from vimiv.commands import commands, cmdexc
from vimiv.modes import modehandler


class Runner(QObject):
    """Base class for command runner objects.

    Signals:
        exited: Emitted when a command exits.
    """

    exited = pyqtSignal(int, str)

    @abc.abstractmethod
    def __call__(self, text):
        """Run the command for a given string of text."""


class CommandRunner(Runner):
    """Runner for internal commands."""

    def __call__(self, text):
        """Run internal command when called.

        Splits the given text into count, name and arguments. Then runs the
        command corresponding to name with count and arguments. Emits the
        exited signal when done.

        Args:
            text: String passed as command.
        """
        mode = modehandler.current().lower()
        count, cmdname, args = self._parse(text)
        try:
            cmd = commands.get(cmdname, mode)
            cmd(args)
            self.exited.emit(0, "")
        except cmdexc.CommandNotFound as e:
            self.exited.emit(1, str(e))
        except (cmdexc.ArgumentError, cmdexc.CommandError) as e:
            self.exited.emit(1, "%s: %s" % (cmdname, str(e)))
        except cmdexc.CommandWarning as w:
            self.exited.emit(2, str(w))

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
