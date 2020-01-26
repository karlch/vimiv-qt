# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.log."""

import pytest

from vimiv.utils import log


@pytest.fixture(autouse=True)
def clean_module_loggers():
    """Fixture to remove any created module loggers."""
    init_loggers = dict(log._module_loggers)
    yield
    for logger in dict(log._module_loggers):
        if logger not in init_loggers:
            del log._module_loggers[logger]


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
