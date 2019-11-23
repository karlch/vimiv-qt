# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Provides functions and signals to handle a shared trash directory.

The functions delete and undeletes images from the user's Trash directory
in $XDG_DATA_HOME/Trash according to the freedesktop.org trash specification.

Module Attributes:
    _files_directory: String path to the directory in which trashed files are
        stored.
    _info_directory: String path to the directory in which info files for
        trashed files are stored.
    _last_deleted: List of last deleted images to allow undeleting them.
"""

import configparser
import os
import shutil
import tempfile
import time
from functools import lru_cache
from typing import cast, Tuple, List

from vimiv import api
from vimiv.utils import xdg


_files_directory = cast(str, None)
_info_directory = cast(str, None)
_last_deleted: List[str] = []


def init() -> None:
    """Create the necessary directories."""
    global _files_directory, _info_directory
    _files_directory = xdg.user_data_dir("Trash", "files")
    _info_directory = xdg.user_data_dir("Trash", "info")
    xdg.makedirs(_files_directory, _info_directory)


@api.keybindings.register("x", "delete %")
@api.commands.register()
def delete(paths: List[str]) -> None:
    """Move one or more paths to the trash directory.

    **syntax:** ``:delete path [path ...]``

    positional arguments:
        * ``paths``: The path(s) to delete.
    """
    _last_deleted.clear()
    for filename in paths:
        filename = os.path.abspath(filename)
        if not os.path.exists(filename):
            raise api.commands.CommandError(f"Path '{filename}' does not exist")
        trash_filename = _get_trash_filename(filename)
        _create_info_file(trash_filename, filename)
        shutil.move(filename, trash_filename)
        _last_deleted.append(os.path.basename(trash_filename))


@api.commands.register()
def undelete(basenames: List[str]) -> None:
    """Restore a file from the trash directory.

    **syntax:** ``:undelete [basename ...]``

    If no basename is given, the last deleted images in this session are restored.

    positional arguments:
        * ``basenames``: The basename(s) of the file in the trash directory.
    """
    basenames = basenames if basenames else _last_deleted
    for basename in basenames:
        trash_filename = os.path.join(_files_directory, basename)
        info_filename = _get_info_filename(basename)
        if not os.path.exists(info_filename) or not os.path.exists(trash_filename):
            raise api.commands.CommandError(f"File for {basename} does not exist")
        original_filename, _ = trash_info(basename)
        if not os.path.isdir(os.path.dirname(original_filename)):
            raise api.commands.CommandError(
                f"Original directory of {basename} is not accessible"
            )
        shutil.move(trash_filename, original_filename)
        os.remove(info_filename)


def _get_trash_filename(filename: str) -> str:
    """Return the name of the file in self.files_directory.

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


def _get_info_filename(filename: str) -> str:
    basename = os.path.basename(filename)
    return os.path.join(_info_directory, basename + ".trashinfo")


def _create_info_file(trash_filename: str, original_filename: str) -> None:
    """Create file with information as specified by the standard.

    Args:
        trash_filename: The name of the file in self.files_directory.
        original_filename: The original name of the file.
    """
    # Note: we cannot use configparser here as it writes keys in lowercase
    info_path = _get_info_filename(trash_filename)
    # Write to temporary file and use shutil.move to make sure the
    # operation is an atomic operation as specified by the standard
    fd, temp_path = tempfile.mkstemp(dir=_info_directory)
    os.close(fd)
    temp_file = open(temp_path, "w")
    temp_file.write("[Trash Info]\n")
    temp_file.write(f"Path={original_filename}\n")
    temp_file.write("DeletionDate={date}\n".format(date=time.strftime("%Y%m%dT%H%M%S")))
    # Make sure that all data is on disk
    temp_file.flush()
    os.fsync(temp_file.fileno())
    temp_file.close()
    shutil.move(temp_path, info_path)


@lru_cache(None)
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
    info_filename = _get_info_filename(filename)
    info = configparser.ConfigParser()
    info.read(info_filename)
    content = info["Trash Info"]
    original_filename = content["Path"]
    deletion_date = content["DeletionDate"]
    return original_filename, deletion_date


def files_directory() -> str:
    return _files_directory
