# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Provides functions and signals to handle a shared trash directory.

The functions delete and undeletes images from the user's Trash directory
in $XDG_DATA_HOME/Trash according to the freedesktop.org trash specification.

Module Attributes:
    _files_directory: Path to the directory in which trashed files are stored.
    _info_directory: Path to the directory in which info files for trashed files are
        stored.
"""

import configparser
import functools
import os
import shutil
import tempfile
import time
from typing import cast, Tuple

from vimiv.utils import xdg


_files_directory = cast(str, None)
_info_directory = cast(str, None)


def init() -> None:
    """Create the necessary directories."""
    global _files_directory, _info_directory
    _files_directory = xdg.user_data_dir("Trash", "files")
    _info_directory = xdg.user_data_dir("Trash", "info")
    xdg.makedirs(_files_directory, _info_directory)


def delete(filename: str) -> str:
    """Move filename to the trash directory.

    Args:
        filename: Name of the file to move to the trash directory.
    Returns:
        The path to the file in the trash directory.
    """
    filename = os.path.abspath(filename)
    trash_filename = _get_trash_filename(filename)
    _create_info_file(trash_filename, filename)
    shutil.move(filename, trash_filename)
    return trash_filename


def undelete(basename: str) -> str:
    """Restore basename from the trash directory.

    Args:
        basename: Basename of the file in the trash directory.
    Returns:
        The path to the restored file.
    """
    trash_filename = os.path.join(_files_directory, basename)
    info_filename = _get_info_filename(basename)
    if not os.path.exists(info_filename) or not os.path.exists(trash_filename):
        raise FileNotFoundError(f"File for '{basename}' does not exist")
    original_filename, _ = trash_info(basename)
    if not os.path.isdir(os.path.dirname(original_filename)):
        raise FileNotFoundError(f"Original directory of '{basename}' is not accessible")
    shutil.move(trash_filename, original_filename)
    os.remove(info_filename)
    return original_filename


@functools.lru_cache(None)
def trash_info(filename: str) -> Tuple[str, str]:
    """Get information stored in the .trashinfo file.

    Uses the lru_cache from functools as opening the files and reading information from
    them is rather expensive.

    Args:
        filename: Name of the file to get info on.
    Returns:
        original_filename: The absolute path to the original file.
        deletion_date: The deletion date.
    """
    from urllib.parse import unquote

    info_filename = _get_info_filename(filename)
    info = TrashInfoParser()
    info.read(info_filename)
    content = info["Trash Info"]
    original_filename = unquote(content["Path"])
    deletion_date = content["DeletionDate"]
    return original_filename, deletion_date


def files_directory() -> str:
    return _files_directory


def _get_trash_filename(filename: str) -> str:
    """Return the name of the file in the trash files directory.

    Args:
        filename: The original name of the file.
    """
    path = os.path.join(_files_directory, os.path.basename(filename))
    # Ensure that we do not overwrite any files
    extension = 2
    original_path = path
    while os.path.exists(path):
        path = original_path + "." + str(extension)
        extension += 1
    return path


def _get_info_filename(trash_filename: str) -> str:
    """Return the name of the corresponding trashinfo file.

    Args:
        trash_filename: The name of the corresponding file in the trash files directory.
    """
    basename = os.path.basename(trash_filename)
    return os.path.join(_info_directory, basename + ".trashinfo")


def _create_info_file(trash_filename: str, original_filename: str) -> None:
    """Create file with information as specified by the standard.

    Args:
        trash_filename: The name of the file in self.files_directory.
        original_filename: The original name of the file.
    """
    from urllib.parse import quote

    # Write to temporary file and use shutil.move to make sure the
    # operation is an atomic operation as specified by the standard
    temp_file = tempfile.NamedTemporaryFile(dir=_info_directory, delete=False, mode="w")
    info = TrashInfoParser()
    info["Trash Info"] = {
        "Path": quote(original_filename),
        "DeletionDate": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    info.write(temp_file, space_around_delimiters=False)
    # Move to proper filename
    info_filename = _get_info_filename(trash_filename)
    shutil.move(temp_file.name, info_filename)


class TrashInfoParser(configparser.ConfigParser):
    """Case-sensitive configparser without interpolation."""

    def __init__(self) -> None:
        super().__init__(interpolation=None)

    def optionxform(self, optionstr: str) -> str:
        """Override so the parser becomes case sensitive."""
        return optionstr
