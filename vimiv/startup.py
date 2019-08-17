# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Main function and startup utilities for vimiv.

Module Attributes:
    _tmpdir: TemporaryDirectory when running with ``--temp-basedir``. The
        object must exist until vimiv exits.
"""

import logging
import logging.handlers
import os
import sys
import tempfile

from PyQt5.QtWidgets import QApplication

from vimiv import app, api, parser, imutils, plugins, version, gui
from vimiv.completion import completionmodels
from vimiv.config import configfile, keyfile, styles
from vimiv.utils import xdg, crash_handler, statusbar_loghandler, trash_manager

# Must be imported to create the commands using the decorators
from vimiv.commands import misccommands  # pylint: disable=unused-import


_tmpdir = None


def main():
    """Run startup and the Qt main loop."""
    args = setup_pre_app(sys.argv[1:])
    qapp = app.Application()
    crash_handler.CrashHandler(qapp)
    setup_post_app(args)
    logging.debug("Startup completed, starting Qt main loop")
    returncode = qapp.exec_()
    plugins.cleanup()
    logging.debug("Exiting with status %d", returncode)
    return returncode


def setup_pre_app(argv):
    """Early setup that is done before the QApplication is created.

    Includes parsing the command line and setting up logging as well as initializing the
    components that do not require an application.

    Args:
        argv: sys.argv[1:] from the executable or argv passed by test suite.
    """
    args = parser.get_argparser().parse_args(argv)
    if args.version:
        print(version.info())
        sys.exit(0)
    init_directories(args)
    setup_logging(args.log_level)
    logging.debug("Start: vimiv %s", " ".join(argv))
    logging.debug("%s\n", version.info())
    logging.debug("%s\n", version.paths())
    update_settings(args)
    trash_manager.init()
    return args


def setup_post_app(args):
    """Setup performed after creating the QApplication."""
    api.working_directory.init()
    api.mark.watch()
    imutils.init()
    completionmodels.init()
    init_ui(args)
    plugins.load()
    init_paths(args)


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
    logging.debug("Opening paths")
    try:
        api.open(os.path.abspath(os.path.expanduser(p)) for p in args.paths)
    except api.commands.CommandError:
        logging.debug("init_paths: No valid paths retrieved")
        if api.settings.startup_library.value:
            api.open([os.getcwd()])
    api.status.update()


def init_ui(args):
    """Initialize the Qt UI."""
    logging.debug("Initializing UI")
    mw = gui.MainWindow()
    if args.fullscreen:
        mw.fullscreen()
    # Center on screen and apply size
    screen_geometry = QApplication.desktop().screenGeometry()
    geometry = (
        args.geometry
        if args.geometry
        else parser.Geometry(screen_geometry.width() / 2, screen_geometry.height() / 2)
    )
    x = screen_geometry.x() + (screen_geometry.width() - geometry.width) // 2
    y = screen_geometry.y() + (screen_geometry.height() - geometry.height) // 2
    mw.setGeometry(x, y, *geometry)
    mw.show()


def update_settings(args):
    """Update default settings with command line arguments and configfiles.

    Args:
        args: Arguments returned from parser.parse_args().
    """
    configfile.parse(args)
    keyfile.parse(args)
    styles.parse()
    for option, value in args.cmd_settings:
        try:
            setting = api.settings.get(option)
            setting.value = value
        except KeyError:
            logging.error("Unknown setting %s", option)
        except ValueError as e:
            logging.error(str(e))
