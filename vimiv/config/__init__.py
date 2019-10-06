# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to store, read and change configurations."""

import configparser
import logging
import sys


def read_log_exception(
    parser: configparser.ConfigParser, logger: logging.Logger, *files: str
) -> None:
    """Read configuration files using parser logging any critical exceptions.

    This is used by the various parsers for consistency in the error message and
    behaviour.

    Args:
        parser: Configparser object used to read the configuration files.
        logger: Logger object used to log the critical exception.
        files: Configuration files to read.
    """
    try:
        parser.read(files)
    except configparser.Error as e:
        logger.critical(
            "Error reading configuration file:\n\n"
            "%s\n%s\n\n"
            "Please fix the file :)\n"
            "See "
            "https://docs.python.org/library/configparser.html#exceptions for help.\n"
            "If you are unsure how to proceed, please file a bug report.",
            type(e),
            e,
        )
        sys.exit(2)
