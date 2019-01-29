# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Main function and startup utilities for vimiv.

Module Attributes:
    _tmpdir: TemporaryDirectory when running with ``--temp-basedir``. The
        object must exist until vimiv exits.
"""

import argparse
import logging
import logging.handlers
import os
import signal
import sys
import tempfile

from PyQt5.QtWidgets import QApplication

import vimiv
from vimiv import app, api, apimodules, parsertypes
from vimiv.completion import completionmodels
from vimiv.config import configfile, keyfile, styles
from vimiv.gui import mainwindow
from vimiv.imutils import iminitialize
from vimiv.utils import (
    xdg,
    clipboard,
    statusbar_loghandler,
    strconvert,
    trash_manager,
    working_directory,
    libpaths,
)


_tmpdir = None


def startup(argv):
    """Run the functions to set up everything.

    Args:
        argv: sys.argv[1:] from the executable.
    """
    # Parse args
    parser = get_argparser()
    args = parser.parse_args(argv)
    # Setup directories
    init_directories(args)
    # Setup logging
    setup_logging(args.log_level)
    logging.info("Start: vimiv %s", " ".join(argv))
    # Parse settings
    configfile.parse(args)
    keyfile.parse(args)
    styles.parse()
    update_settings(args)
    # Objects needed before UI
    earlyinit()
    # Set up UI
    init_ui(args)
    # Open paths
    init_paths(args)
    # Finalize
    logging.info("Startup completed")
    api.status.update()


def earlyinit():
    """Initialize objects needed as early as possible."""
    clipboard.init()
    trash_manager.init()
    working_directory.init()
    libpaths.init()
    iminitialize.init()
    apimodules.init()
    completionmodels.init()


def setup_logging(log_level):
    """Prepare the python logging module.

    Sets it up to write to stderr and $XDG_DATA_HOME/vimiv/vimiv.log.

    Args:
        log_level: Log level as string as given from the command line.
    """
    log_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S"
    )

    logger = logging.getLogger()
    logger.handlers = []
    logger.setLevel(log_level)

    file_handler = logging.FileHandler(xdg.join_vimiv_data("vimiv.log"), mode="w")
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    sb_handler = statusbar_loghandler.StatusbarLogHandler()
    logger.addHandler(sb_handler)


def get_argparser():
    """Get the argparse parser."""
    parser = argparse.ArgumentParser(
        prog=vimiv.__name__, description=vimiv.__description__
    )
    parser.add_argument(
        "-f", "--fullscreen", action="store_true", help="Start fullscreen"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="vimiv version %s" % vimiv.__version__,
        help="Print version information and exit",
    )
    parser.add_argument(
        "--slideshow", action="store_true", help="Start slideshow at start-up"
    )
    parser.add_argument(
        "-g",
        "--geometry",
        type=parsertypes.geometry,
        metavar="WIDTHxHEIGHT",
        help="Set the starting geometry",
    )
    parser.add_argument(
        "--temp-basedir", action="store_true", help="Use a temporary basedir"
    )
    parser.add_argument(
        "--config",
        type=parsertypes.existing_file,
        metavar="FILE",
        help="Use FILE as local configuration file",
    )
    parser.add_argument(
        "--keyfile",
        type=parsertypes.existing_file,
        metavar="FILE",
        help="Use FILE as keybinding file",
    )
    parser.add_argument(
        "-s",
        "--set",
        nargs=2,
        default=[],
        action="append",
        dest="cmd_settings",
        metavar=("OPTION", "VALUE"),
        help="Set a temporary setting",
    )
    parser.add_argument(
        "--log-level",
        type=parsertypes.loglevel,
        metavar="LEVEL",
        help="Set log level to LEVEL",
        default="warning",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=parsertypes.existing_path,
        metavar="PATH",
        help="Paths to open",
    )
    return parser


def init_directories(args):
    """Create vimiv cache, config and data directories.

    The directories are either the directories defined in the freedesktop
    standard or located in a temporary base directory.

    Args:
        args: Arguments returned from parser.parse_args().
    """
    if args.temp_basedir:
        global _tmpdir
        _tmpdir = tempfile.TemporaryDirectory(prefix="vimiv-tempdir-")
        basedir = _tmpdir.name
        os.environ["XDG_CACHE_HOME"] = os.path.join(basedir, "cache")
        os.environ["XDG_CONFIG_HOME"] = os.path.join(basedir, "config")
        os.environ["XDG_DATA_HOME"] = os.path.join(basedir, "data")
    for directory in [
        xdg.vimiv_cache_dir(),
        xdg.vimiv_config_dir(),
        xdg.vimiv_data_dir(),
        xdg.join_vimiv_config("styles"),
    ]:
        os.makedirs(directory, exist_ok=True)


def init_paths(args):
    """Open paths given from commandline or fallback to library if set."""
    if not app.open_paths(args.paths) and api.settings.STARTUP_LIBRARY.value:
        app.open_paths([os.getcwd()])


def init_ui(args):
    """Initialize the Qt UI."""
    mw = mainwindow.MainWindow()
    mw.show()
    if args.fullscreen:
        mw.fullscreen()
    # Center on screen and apply size
    screen_geometry = QApplication.desktop().screenGeometry()
    geometry = (
        args.geometry
        if args.geometry
        else parsertypes.Geometry(
            screen_geometry.width() / 2, screen_geometry.height() / 2
        )
    )
    x = (screen_geometry.width() - geometry.width) // 2
    y = (screen_geometry.height() - geometry.height) // 2
    mw.setGeometry(x, y, *geometry)


def update_settings(args):
    """Update settings in storage with arguments from command line.

    Args:
        args: Arguments returned from parser.parse_args().
    """
    for option, value in args.cmd_settings:
        try:
            api.settings.override(option, value)
        except KeyError:
            logging.error("Unknown setting %s", option)
        except strconvert.ConversionError as e:
            logging.error(str(e))


def main():
    """Run startup and the Qt main loop."""
    qapp = app.Application()
    startup(sys.argv[1:])
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # ^C
    return qapp.exec_()
