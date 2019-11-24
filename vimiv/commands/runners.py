# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes and functions to run commands.

Module Attributes:
    SEPARATOR: String used to separate chained commands.

    _last_command: Dictionary storing the last command for each mode.
"""

import re
import shlex
from typing import Dict, List, NamedTuple, Tuple

from vimiv import api, utils
from vimiv.utils import log, customtypes
from vimiv.commands import aliases

from .external import ExternalRunner


SEPARATOR = "&&"
external = ExternalRunner()

_last_command: Dict[api.modes.Mode, "LastCommand"] = {}
_logger = log.module_logger(__name__)


class LastCommand(NamedTuple):
    """Simple class storing command text, arguments and count."""

    Count: str
    Command: str
    Arguments: List[str]


class CommandPartFailed(Exception):
    """Raised if a command part fails, e.g. due to the command being unknown."""


def text_non_whitespace(func: customtypes.FuncNoneT) -> customtypes.FuncNoneT:
    """Decorator to only run function if text argument is more than plain whitespace."""

    def inner(text: str, *args, **kwargs) -> None:
        text = text.strip()
        if not text:
            return None
        return func(text, *args, **kwargs)

    # Mypy seems to disapprove the *args, **kwargs, but we just wrap the function
    return inner  # type: ignore


@text_non_whitespace
def run(text: str, mode: api.modes.Mode, count: str = "") -> None:
    """Run a (chain of) command(s).

    The text to run is split at SEPARATOR and each part is handled individually by
    _run_single. If one part fails, the remaining parts are not executed.

    Args:
        text: Complete text given to command line or keybinding.
        mode: Mode to run the command in.
        count: Count given if any.
    """
    _logger.debug("Running '%s'", text)

    def update_part(text: str) -> str:
        """Update aliases and % in final parts without seperator."""
        if SEPARATOR in text:
            return text
        return expand_percent(alias(text.strip(), mode), mode)

    textparts = utils.recursive_split(text, SEPARATOR, update_part)
    _logger.debug("Split text into parts '%s'", textparts)
    try:
        for i, cmdpart in enumerate(textparts):
            _logger.debug("Handling part %d '%s'", i, cmdpart)
            _run_single(cmdpart, mode, count)
    except CommandPartFailed:
        _logger.debug("Stopping at %d as '%s' failed", i, cmdpart)


@text_non_whitespace
def _run_single(text: str, mode: api.modes.Mode, count: str) -> None:
    """Run either external or internal command.

    Args:
        text: Complete text given to command line or keybinding.
        count: Count given if any.
        mode: Mode to run the command in.
    """
    if text.startswith("!"):
        external.run(text.lstrip("!"))
    else:
        command(count + text, mode)


def command(text: str, mode: api.modes.Mode = None) -> None:
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
def repeat_command(count: str = None) -> None:
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


def _run_command(
    count: str, cmdname: str, args: List[str], mode: api.modes.Mode
) -> None:
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
        api.status.update("ran command")
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


def _parse(text: str) -> Tuple[str, str, List[str]]:
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


def expand_percent(text: str, mode: api.modes.Mode) -> str:
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


def alias(text: str, mode: api.modes.Mode) -> str:
    """Replace alias with the actual command.

    Returns:
        The replaced text if text was an alias else text.
    """
    cmd = text.split()[0]
    if cmd in aliases.get(mode):
        text = text.replace(cmd, aliases.get(mode)[cmd])
        return expand_percent(text, mode)
    return text
