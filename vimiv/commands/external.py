# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Functions to interact with the shell."""

import subprocess

from vimiv.commands import commands


def run(text):
    """Run external command using subprocess.run.

    Captures stdout and stderr. The commands.signals.exited signal is emitted
    depending on the returncode of the command.

    Args:
        text: Text parsed as command to run.
    """
    try:
        subprocess.run(text, shell=True, check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        commands.signals.exited.emit(0, "")
    except subprocess.CalledProcessError as e:
        message = e.stderr.decode().split("\n")[0]
        commands.signals.exited.emit(e.returncode, message)
