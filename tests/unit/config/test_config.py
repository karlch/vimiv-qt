# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Unit tests for vimiv.config."""

import configparser

import pytest

from vimiv import config
from vimiv.utils import customtypes


@pytest.mark.parametrize(
    "content, message",
    [
        ("GIBBERISH\n", "missing section header"),
        ("[SECTION]\nvalue", "key missing value"),
        ("[]\n", "empty section name"),
        ("[SECTION\n", "only opening section bracket"),
        ("SECTION]\n", "only closing section bracket"),
        ("[SECTION]\n[SECTION]\n", "duplicate section"),
        ("[SECTION]\na=0\na=1\n", "duplicate key"),
    ],
)
def test_sysexit_on_broken_config(mocker, tmp_path, content, message):
    """Ensure SystemExit is correctly raised for various broken config files.

    Args:
        content: Content written to the configuration file which is invalid.
        message: Message printed to help debugging.
    """
    print("Ensuring system exit with", message)
    mock_logger = mocker.Mock()
    parser = configparser.ConfigParser()
    path = tmp_path / "configfile"
    path.write_text(content)
    with pytest.raises(SystemExit, match=str(customtypes.Exit.err_config)):
        config.read_log_exception(parser, mock_logger, str(path))
    mock_logger.critical.assert_called_once()
