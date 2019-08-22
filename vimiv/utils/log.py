# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utilities related to logging.

Module Attributes:
    _module_loggers: Dictionary mapping module names to their corresponding logger.
"""

import logging
import logging.handlers
from typing import Dict

import vimiv

from ._statusbar_loghandler import handler as statusbar_loghandler
from . import xdg


_module_loggers: Dict[str, logging.Logger] = {}


def debug(msg: str, *args, **kwargs) -> None:
    """Log a debug message using the application-wide logger."""
    logging.getLogger(vimiv.__name__).debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Log an info message using the application-wide logger."""
    logging.getLogger(vimiv.__name__).info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """Log a warning message using the application-wide logger."""
    logging.getLogger(vimiv.__name__).warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """Log an error message using the application-wide logger."""
    logging.getLogger(vimiv.__name__).error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """Log a critical message using the application-wide logger."""
    logging.getLogger(vimiv.__name__).critical(msg, *args, **kwargs)


def setup_logging(level: int, *debug_modules: str) -> None:
    """Configure and set up logging.

    There are two types of loggers: the application-wide logger accessible through the
    convenience functions and the module-level loggers. Both loggers write to stderr and
    $XDG_DATA_HOME/vimiv/vimiv.log. The application-wide logger sends messages with a
    level higher than debug to the statusbar in addition.

    All log messages are always sent to the log file. The level for the console and
    statusbar handlers depend on the level passed to this function.

    No logging should be performed in this function as the logging header comes directly
    after it.

    Args:
        level: Integer log level set for the console handler.
        debug_modules: Module names for which debug messages are forced to be shown.
    """
    # Configure the root logger
    formatter = logging.Formatter(
        "[{asctime}] {levelname:8} {message}", datefmt="%H:%M:%S", style="{"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(xdg.join_vimiv_data("vimiv.log"))
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [file_handler, console_handler, statusbar_loghandler]

    root_logger.setLevel(logging.DEBUG)
    console_handler.setLevel(level)
    statusbar_loghandler.setLevel(level)
    # Setup debug logging for specific modules
    for name, logger in _module_loggers.items():
        logger.handlers[1].setLevel(logging.DEBUG if name in debug_modules else level)


def module_logger(name: str) -> logging.Logger:
    """Create a module-level logger.

    Module-level loggers log to the vimiv log-file as well as the console. Their
    formatter is slightly different from the application-wide on by also printing the
    name of the module.

    Args:
        name: Name of the module for which the logger is created.
    Returns:
        The created logger object.
    """
    name = name.replace("vimiv.", "")

    if name in _module_loggers:
        return _module_loggers[name]

    formatter = logging.Formatter(
        "[{asctime}] {levelname:8} {name:20} {message}", datefmt="%H:%M:%S", style="{"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(xdg.join_vimiv_data("vimiv.log"))
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(f"<{name}>")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers = [file_handler, console_handler]

    _module_loggers[name] = logger
    return logger
