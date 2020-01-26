# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.log."""

import logging

import pytest

from vimiv.utils import log


@pytest.fixture(autouse=True)
def clean_module_loggers():
    """Fixture to remove any created module loggers."""
    init_loggers = dict(log._module_loggers)
    init_debug_loggers = list(log._debug_loggers)
    yield
    for logger in dict(log._module_loggers):
        if logger not in init_loggers:
            del log._module_loggers[logger]
    for logger in set(log._debug_loggers) - set(init_debug_loggers):
        log._debug_loggers.remove(logger)


@pytest.fixture
def lazy_logger():
    """Fixture to retrieve a clean lazy logger instance."""
    return log.LazyLogger("test.logger")


@pytest.fixture
def setup_logging():
    """Fixture to setup logging appropriately."""
    log.setup_logging(logging.WARNING)


@pytest.mark.parametrize("name", ("vimiv.module", "other.module"))
def test_module_logger_name(name):
    expected = name.replace("vimiv.", "")
    logger = log.module_logger(name)
    assert logger._name == expected


def test_lazy_logger_is_lazy(setup_logging, lazy_logger):
    """Ensure lazy logger is only created when a message above its level is logged."""
    message = "Random log statement"
    lazy_logger.debug(message)
    assert lazy_logger._logger is None  # Not created for debug message
    lazy_logger.warning(message)
    assert lazy_logger._logger is not None  # Created by warning message


def test_lazy_logger_logs(capsys, setup_logging, lazy_logger):
    """Ensure lazy logger logs messages as expected."""
    message = "Random log statement"
    lazy_logger.debug(message)
    captured = capsys.readouterr()
    assert message not in captured.err
    lazy_logger.warning(message)
    captured = capsys.readouterr()
    assert message in captured.err


@pytest.mark.parametrize("creation_time", ("before", "after"))
def test_setup_logging_debug_loggers(capsys, creation_time):
    """Ensure debug loggers are created with the debug level and log debug messages.

    Creation time defines if the debug logger is created before setting up logging
    (usual case) or afterwards (the case for lazy imported modules).
    """
    name = "my.module.logger"
    if creation_time == "before":
        module_logger = log.module_logger(name)
    log.setup_logging(logging.WARNING, name)
    if creation_time == "after":
        module_logger = log.module_logger(name)

    message = "Show this debug statement"
    module_logger.debug(message)
    captured = capsys.readouterr()

    assert module_logger.level == logging.DEBUG
    assert message in captured.err


@pytest.mark.parametrize(
    "level",
    (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL),
)
def test_module_logger_level_after_setup(capsys, level):
    """Ensure module loggers are created with global app level."""
    log.setup_logging(level)
    module_logger = log.module_logger("my.module.logger")

    message = "Show this debug statement"
    module_logger.log(level, message)
    captured = capsys.readouterr()

    assert module_logger.level == level
    assert message in captured.err
