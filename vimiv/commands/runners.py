# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import shlex
import subprocess

from PyQt5.QtCore import pyqtSignal, QObject

from vimiv.commands import commands, cmdexc


class Signals(QObject):
    """Signals used by command runner objects.

    Signals:
        exited: Emitted when a command exits.
    """

    exited = pyqtSignal(int, str)


signals = Signals()


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
            signals.exited.emit(0, "")
        except cmdexc.CommandNotFound as e:
            signals.exited.emit(1, str(e))
        except (cmdexc.ArgumentError, cmdexc.CommandError) as e:
            signals.exited.emit(1, "%s: %s" % (cmdname, str(e)))
        except cmdexc.CommandWarning as w:
            signals.exited.emit(2, str(w))

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


class ExternalRunner():
    """Runner for external commands."""

    def __call__(self, text):
        """Run external command using subprocess.run.

        Captures stdout and stderr. The signals.exited signal is emitted
        depending on the returncode of the command.

        Args:
            text: Text parsed as command to run.
        """
        try:
            subprocess.run(text, shell=True, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            signals.exited.emit(0, "")
        except subprocess.CalledProcessError as e:
            message = e.stderr.decode().split("\n")[0]
            signals.exited.emit(e.returncode, message)
