# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Utilities related to logging`.

There are two different types of loggers: the application-wide logger and module
specific loggers.

The application-wide logger is used for general messages meant for the user. All log
messages with level larger than debug are also sent to the statusbar. To send a message
to this logger, the utility functions :func:`debug`, :func:`info`, :func:`warning`,
:func:`error` and :func:`critical` can be used. They are just very thin wrapper
functions around the python logging functions.

For debugging it is recommended to use a module specific logger. This allows fine-tuning
the amount of debug statements that should be displayed using the ``--debug`` flag. To
create a module logger::

    from vimiv.utils import log

    _logger = log.module_logger(__name__)

and use this logger as usual::

    _logger.debug("Performing some setup")
    ...
    _logger.debug("Doing the work")
    ...
    _logger.debug("Performing some clean-up")

Three log handlers are currently used:

* One to print to the console
* One to save the output in a log file located in
  ``$XDG_DATA_HOME/vimiv/vimiv.log``
* One to print log messages to the statusbar (only for application-wide logger)

Module Attributes:
    statusbar_loghandler: Instance of the log handler connecting to the statusbar.

    _module_loggers: Dictionary mapping module names to their corresponding logger.
"""

import logging
import logging.handlers
from typing import Dict

from PyQt5.QtCore import pyqtSignal, QObject

import vimiv

from . import xdg


_module_loggers: Dict[str, logging.Logger] = {}
formatter = logging.Formatter(
    "[{asctime}] {levelname:8} {name:20} {message}", datefmt="%H:%M:%S", style="{"
)


def debug(msg: str, *args, **kwargs) -> None:
    """Log a debug message using the application-wide logger."""
    logging.getLogger(f"<{vimiv.__name__}>").debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Log an info message using the application-wide logger."""
    logging.getLogger(f"<{vimiv.__name__}>").info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """Log a warning message using the application-wide logger."""
    logging.getLogger(f"<{vimiv.__name__}>").warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """Log an error message using the application-wide logger."""
    logging.getLogger(f"<{vimiv.__name__}>").error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """Log a critical message using the application-wide logger."""
    logging.getLogger(f"<{vimiv.__name__}>").critical(msg, *args, **kwargs)


fatal = critical


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
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    # mode=w creates a new file for every new vimiv process
    file_handler = logging.FileHandler(xdg.join_vimiv_data("vimiv.log"), mode="w")
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [file_handler, console_handler, statusbar_loghandler]

    root_logger.setLevel(logging.DEBUG)
    console_handler.setLevel(level)
    statusbar_loghandler.setLevel(level)
    # Setup debug logging for specific modules
    for name, logger in _module_loggers.items():
        logger.setLevel(logging.DEBUG)  # Activate logger in general
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG if name in debug_modules else level)
        # Append file handler here to ensure logging to one file
        logger.handlers.append(file_handler)


def module_logger(name: str) -> logging.Logger:
    """Create a module-level logger.

    Module-level loggers log to the vimiv log-file as well as the console. The file
    handler is only attached in setup_logging to ensure logging to the correct file,
    even when starting with --temp-basedir.

    Args:
        name: Name of the module for which the logger is created.
    Returns:
        The created logger object.
    """
    name = name.replace("vimiv.", "")

    if name in _module_loggers:
        return _module_loggers[name]

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(f"<{name}>")
    logger.setLevel(logging.CRITICAL)  # No logging before the module has been set up
    logger.propagate = False
    logger.handlers = [console_handler]

    _module_loggers[name] = logger
    return logger


class StatusbarLogHandler(QObject, logging.NullHandler):
    """Loghandler to display log messages in the statusbar.

    Only emits a signal on handle which the statusbar connects to.

    Signals:
        message: Emitted with severity and message on log message.
    """

    message = pyqtSignal(str, str)

    def handle(self, record: logging.LogRecord) -> None:
        if record.levelno >= logging.INFO:  # Debug in the statusbar makes no sense
            self.message.emit(record.levelname.lower(), record.message)


statusbar_loghandler = StatusbarLogHandler()
