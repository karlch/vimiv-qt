# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Check version and availability of required software upon import.

This module is imported first in the top-level __init__.py to ensure we are running with
the correct python and PyQt versions. In case this fails, error messages are written to
stderr and we exit with returncode ERR_CODE.

Module Attributes:
    PYQT_VERSION: The currently installed PyQt version as tuple if any.
    PYQT_REQUIRED_VERSION: The minimum PyQt version required.
    PYTHON_REQUIRED_VERSION: The minimum python version required.
    ERR_CODE: Returncode used with sys.exit.
"""

import sys


PYTHON_REQUIRED_VERSION = (3, 6)
PYQT_REQUIRED_VERSION = (5, 9, 2)
ERR_CODE = 2


def check_python_version():
    """Ensure the python version is new enough."""
    if sys.version_info < PYTHON_REQUIRED_VERSION:
        _exit_version("python", PYTHON_REQUIRED_VERSION, sys.version_info[:3])


def check_pyqt_version():
    """Ensure the PyQt version is new enough."""
    try:
        from vimiv.qt.core import PYQT_VERSION_STR
    except ImportError as e:  # TODO add back test for this
        _exit(
            f"Error importing a valid Qt python wrapper:\n{e}\n\n"
            "Please install / configure a valid wrapper to run vimiv.\n"
        )

    pyqt_version = tuple(map(int, PYQT_VERSION_STR.split(".")))
    if pyqt_version < PYQT_REQUIRED_VERSION:
        _exit_version("PyQt", PYQT_REQUIRED_VERSION, pyqt_version)


def join_version_tuple(version):
    return ".".join(map(str, version))


def _exit_version(software, required, installed):
    """Call exit for out-of-date software."""
    # This module needs to work for python < 3.6
    # pylint: disable=consider-using-f-string
    _exit(
        "At least %s %s is required to run vimiv. Using %s.\n"
        % (software, join_version_tuple(required), join_version_tuple(installed))
    )


def _exit(message):
    """Write message to stderr and exit with returncode 1."""
    sys.stderr.write(message)
    sys.stderr.flush()
    sys.exit(ERR_CODE)


check_python_version()
check_pyqt_version()
