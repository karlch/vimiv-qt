# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Miscellaneous commands that don't really fit anywhere."""

import logging
import time
from typing import List

from vimiv import api, utils


_logger = utils.log.module_logger(__name__)


@api.commands.register()
def log(level: str, message: List[str]):
    """Log a message with the corresponding log level.

    **syntax:** ``:log level message``

    positional arguments:
        * ``level``: Log level of the message (debug, info, warning, error, critical).
        * ``message``: Message to log.
    """
    try:
        log_level = getattr(logging, level.upper())
    except AttributeError:
        raise api.commands.CommandError(f"Unknown log level '{level}'")
    utils.log.log(log_level, " ".join(message))


@api.commands.register()
def sleep(duration: float):
    """Sleep for a given number of seconds.

    **syntax:** ``:sleep duration``

    positional arguments:
        * ``duration``: The number of seconds to sleep.
    """
    _logger.debug("Sleeping for %.2f seconds, good-night :)", duration)
    time.sleep(duration)
    _logger.debug("Woke up nice and refreshed!")
