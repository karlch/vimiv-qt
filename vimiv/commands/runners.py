# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes and functions to run commands.

Module Attributes:
    SEPARATOR: String used to separate chained commands.
    external: ExternalRunner instance to run shell commands.

    _last_command: Dictionary storing the last command for each mode.
"""

import os
import re
import shlex
import subprocess
from typing import Dict, List, NamedTuple, Optional, Callable

from vimiv import api, utils
from vimiv.utils import log, asyncfunc
from vimiv.commands import aliases


SEPARATOR = "&&"

_last_command: Dict[api.modes.Mode, "LastCommand"] = {}
_logger = log.module_logger(__name__)


class LastCommand(NamedTuple):
    """Simple class storing command text, arguments and count."""

    Count: int
    Command: str
    Arguments: List[str]


class CommandPartFailed(Exception):
    """Raised if a command part fails, e.g. due to the command being unknown."""


def text_non_whitespace(func: Callable[..., None]):
    """Decorator to only run function if text argument is more than plain whitespace."""

    def inner(text: str, *args, **kwargs) -> None:
        text = text.strip()
        if not text:
            return None
        return func(text, *args, **kwargs)

    return inner


@text_non_whitespace
def run(text, count=None, mode=None):
    """Run a (chain of) command(s).

    The text to run is split at SEPARATOR and each part is handled individually by
    _run_single. If one part fails, the remaining parts are not executed.

    Args:
        text: Complete text given to command line or keybinding.
        count: Count given if any.
        mode: Mode to run the command in.
    """
    _logger.debug("Running '%s'", text)

    def update_part(text):
        """Update aliases and % in final parts without seperator."""
        if SEPARATOR in text:
            return text
        return expand_percent(alias(text.strip(), mode), mode)

    textparts = utils.recursive_split(text, SEPARATOR, update_part)
    _logger.debug("Split text into parts '%s'", textparts)
    try:
        for i, cmdpart in enumerate(textparts):
            _logger.debug("Handling part %d '%s'", i, cmdpart)
            _run_single(cmdpart, count, mode)
    except CommandPartFailed:
        _logger.debug("Stopping at %d as '%s' failed", i, cmdpart)


@text_non_whitespace
def _run_single(text, count=None, mode=None):
    """Run either external or internal command.

    Args:
        text: Complete text given to command line or keybinding.
        count: Count given if any.
        mode: Mode to run the command in.
    """
    if text.startswith("!"):
        external(text.lstrip("!"))
    else:
        count = str(count) if count is not None else ""
        command(count + text, mode)


def command(text, mode=None):
    """Run internal command when called.

    Splits the given text into count, name and arguments. Then runs the
    command corresponding to name with count and arguments. Emits the
    exited signal when done.

    Args:
        text: String passed as command.
        mode: Mode in which the command is supposed to run.
    """
    try:
        count, cmdname, args = _parse(text)
    except ValueError as e:  # E.g. raised by shlex on unclosed quotation
        log.error("Error parsing command: %s", e)
        return
    mode = mode if mode is not None else api.modes.current()
    _run_command(count, cmdname, args, mode)
    _logger.debug("Ran '%s' succesfully", text)


@api.keybindings.register(".", "repeat-command")
@api.commands.register(store=False)
def repeat_command(count: Optional[int] = None):
    """Repeat the last command.

    **count:** Repeat count times.
    """
    mode = api.modes.current()
    if mode not in _last_command:
        raise api.commands.CommandError("No command to repeat")
    stored_count, cmdname, args = _last_command[mode]
    # Prefer entered count over stored count
    count = count if count is not None else stored_count
    _run_command(count, cmdname, args, mode)


def _run_command(count, cmdname, args, mode):
    """Run a given command.

    Args:
        count: Count to use for the command.
        cmdname: Name of the command passed.
        args: Arguments passed.
        mode: Mode to run the command in.
    """
    try:
        cmd = api.commands.get(cmdname, mode)
        if cmd.store:
            _last_command[mode] = LastCommand(count, cmdname, args)
        cmd(args, count=count)
        api.status.update()
    except api.commands.CommandNotFound as e:
        log.error(str(e))
        raise CommandPartFailed from e
    except (
        api.commands.ArgumentError,
        api.commands.CommandError,
        api.modes.InvalidMode,
    ) as e:
        log.error("%s: %s", cmdname, e)
        raise CommandPartFailed from e
    except api.commands.CommandWarning as w:
        log.warning("%s: %s", cmdname, str(w))
        raise CommandPartFailed from w
    except api.commands.CommandInfo as i:
        log.info("%s: %s", cmdname, i)
        raise CommandPartFailed from i


def _parse(text):
    """Parse given command text into count, name and arguments.

    Args:
        text: String passed as command.
    Returns:
        count: Digits prepending the command to interpret as count.
        name: Name of the command passed.
        args: Arguments passed.
    """
    text = text.strip()
    count = ""
    split = shlex.split(text)
    cmdname = split[0]
    # Receive prepended digits as count
    while cmdname and cmdname[0].isdigit():
        count += cmdname[0]
        cmdname = cmdname[1:]
    args = split[1:]
    return count, cmdname, args


def expand_percent(text, mode):
    """Expand % to the corresponding path and %m to all marked paths.

    Args:
        text: The command in which the wildcards are expanded.
        mode: Mode the command is run in to get correct path(-list).
    """
    # Check first as the re substitutions are rather expensive
    if "%m" in text:
        text = re.sub(r"(?<!\\)%m", " ".join(api.mark.paths), text)
        text = text.replace("\\%m", "%")  # Remove escape characters
    if "%" in text:
        current = shlex.quote(api.current_path(mode))
        text = re.sub(r"(?<!\\)%", current, text)
        text = text.replace("\\%", "%")  # Remove escape characters
    return text


class ExternalRunner:
    """Runner for external commands."""

    @asyncfunc()
    def __call__(self, text: str) -> None:
        """Run external command in parallel.

        Args:
            text: Text parsed as command to run.
        """
        pipe = text.endswith("|")
        text = text.rstrip("|").strip()
        try:
            pargs = subprocess.run(
                text,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if pipe:
                self.process_pipe(text, pargs.stdout.decode())
            else:
                _logger.debug("Ran '!%s' succesfully", text)
        except subprocess.CalledProcessError as e:
            message = e.stderr.decode().split("\n")[0]
            log.error("%d  %s", e.returncode, message)

    def process_pipe(self, cmd: str, stdout: str) -> None:
        """Open paths from stdout.

        Args:
            cmd: Executed shell command.
            stdout: String form of stdout of the exited shell command.
        """
        paths = [path for path in stdout.split("\n") if os.path.exists(path)]
        try:
            api.open(paths)
            _logger.debug("Opened paths from pipe '%s'", cmd)
            api.status.update()
        except api.commands.CommandError:
            log.warning("%s: No paths from pipe", cmd)


external = ExternalRunner()


def alias(text, mode):
    """Replace alias with the actual command.

    Returns:
        The replaced text if text was an alias else text.
    """
    cmd = text.split()[0]
    if cmd in aliases.get(mode):
        text = text.replace(cmd, aliases.get(mode)[cmd])
        return expand_percent(text, mode)
    return text
