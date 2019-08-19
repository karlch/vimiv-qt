# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utilities related to logging."""

import logging
import logging.handlers

from . import statusbar_loghandler, xdg


def setup_logging(log_level):
    """Prepare the python logging module.

    Sets it up to write to stderr and $XDG_DATA_HOME/vimiv/vimiv.log.

    Args:
        log_level: Integer log level set for the console handler.
    """
    log_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S"
    )

    logger = logging.getLogger()
    logger.handlers = []
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(xdg.join_vimiv_data("vimiv.log"), mode="w")
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    statusbar_loghandler.setLevel(log_level)
    logger.addHandler(statusbar_loghandler)
