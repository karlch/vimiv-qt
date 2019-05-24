# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to retrieve various version information.

Module Attributes:
    _license_str: GPL boilerplate including the licensing information.
"""

import sys

from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR

import vimiv
from vimiv.utils import xdg

# Optional imports to check if these features are supported
try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None

try:
    import piexif
except ImportError:
    piexif = None


def info() -> str:
    """Retrieve version information.

    This includes the current vimiv version and python, Qt as well as PyQt versions and
    some information on the optional dependencies.
    """
    return (
        f"vimiv v{vimiv.__version__}\n\n"
        f"Python: {_python_version()}\n"
        f"Qt: {QT_VERSION_STR}\n"
        f"PyQt: {PYQT_VERSION_STR}\n\n"
        f"Svg Support: {bool(QSvgWidget)} \n"
        f"Piexif: {piexif.VERSION if piexif is not None else None}"
    )


def paths() -> str:
    """Retrieve information on relevant paths."""
    return (
        "Paths:\n"
        f"cache: {xdg.vimiv_cache_dir()}\n"
        f"config: {xdg.vimiv_config_dir()}\n"
        f"data: {xdg.vimiv_data_dir()}"
    )


def gpl_boilerplate() -> str:
    """Return GPL boilerplate."""
    return _license_str


def detailed_info() -> str:
    """Return version, paths info and license."""
    return f"{info()}\n\n{paths()}\n\n{gpl_boilerplate()}"


def _python_version() -> str:
    """Return python version as MAJOR.MINOR.MICRO."""
    return "{info.major}.{info.minor}.{info.micro}".format(info=sys.version_info)


_license_str = """License:
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""
