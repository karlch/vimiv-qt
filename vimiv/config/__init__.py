# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to store, read and change configurations."""

import configparser
import os
import sys
from typing import Optional, Callable

from vimiv.utils import xdg, customtypes, log


def parse_config(
    cli_path: Optional[str],
    basename: str,
    read: Callable[[str], None],
    dump: Callable[[str], None],
) -> None:
    """Helper function to parse configuration files.

    If the commandline path is given, it is always used for reading. Otherwise the user
    file is read, if it exists, else a default file is created using dump.

    Args:
        cli_path: Path to configuration file as given from the commandline.
        basename: Basename of the configuration file in vimiv's config directory.
        read: Function to call for reading the configuration file.
        dump: Function to call for writing the configuration file.
    """
    if cli_path is not None:
        read(cli_path)
        return
    user_path = xdg.vimiv_config_dir(basename)
    if os.path.isfile(user_path):  # Read from user configuration file
        read(user_path)
    else:  # Dump defaults
        dump(user_path)


def read_log_exception(
    parser: configparser.ConfigParser, logger: log.LazyLogger, *files: str
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
        sys.exit(customtypes.Exit.err_config)
