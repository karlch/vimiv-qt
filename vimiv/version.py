# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to retrieve various version information.

Module Attributes:
    _license_str: GPL boilerplate including the licensing information.
"""

import os
import sys
from functools import lru_cache
from typing import Optional

from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR

import vimiv
from vimiv.utils import xdg, run_qprocess

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
    git_info = _git_info()
    vimiv_version = (
        f"vimiv v{vimiv.__version__}\n{git_info}"
        if git_info is not None
        else f"vimiv v{vimiv.__version__}"
    )
    return (
        f"{vimiv_version}\n\n"
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


@lru_cache(1)
def _git_info() -> Optional[str]:
    """Return git current commit information if possible else None."""
    gitdir = os.path.realpath(
        os.path.join(os.path.realpath(__file__), os.pardir, os.pardir)
    )
    if not os.path.isdir(os.path.join(gitdir, ".git")):
        return None

    try:
        commit = run_qprocess(
            "git",
            "describe",
            "--match=NoMaTcH",
            "--always",
            "--abbrev=40",
            "--dirty",
            cwd=gitdir,
        )
        date = run_qprocess(
            "git", "show", "-s", "--format=%cd", "--date=short", "HEAD", cwd=gitdir
        )
    except OSError:
        return None
    return f"Git: {commit} ({date})"


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
