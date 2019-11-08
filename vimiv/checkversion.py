# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
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

try:
    from PyQt5.QtCore import PYQT_VERSION_STR

    PYQT_VERSION = tuple(map(int, PYQT_VERSION_STR.split(".")))
except ImportError:  # pragma: no cover  # PyQt is there in tests, using None is tested
    # We check explicitly for None before using the tuple version
    PYQT_VERSION = None  # type: ignore


PYTHON_REQUIRED_VERSION = (3, 6)
PYQT_REQUIRED_VERSION = (5, 9, 2)
ERR_CODE = 2


def check_python_version():
    """Ensure the python version is new enough."""
    if sys.version_info < PYTHON_REQUIRED_VERSION:
        _exit_version("python", PYTHON_REQUIRED_VERSION, sys.version_info[:3])


def check_pyqt_version():
    """Ensure the PyQt version is new enough."""
    if PYQT_VERSION is None:
        _exit("PyQt is required to run vimiv.\n")
    elif PYQT_VERSION < PYQT_REQUIRED_VERSION:
        _exit_version("PyQt", PYQT_REQUIRED_VERSION, PYQT_VERSION)


def join_version_tuple(version):
    return ".".join(map(str, version))


def _exit_version(software, required, installed):
    """Call exit for out-of-date software."""
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
