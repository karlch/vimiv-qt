# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Provides functions and signals to handle a shared trash directory.

The functions delete and undeletes images from the user's Trash directory
in $XDG_DATA_HOME/Trash according to the freedesktop.org trash specification.

Module Attributes:
    signals: Signals class storing signals emitted when deleting/undeleting.

    _files_directory: String path to the directory in which trashed files are
        stored.
    _info_directory: String path to the directory in which info files for
        trashed files are stored.
"""

import configparser
import os
import shutil
import tempfile
import time

from PyQt5.QtCore import QObject, pyqtSignal

# from vimiv.utils.exceptions import TrashUndeleteError
from vimiv.commands import commands, cmdexc
from vimiv.config import keybindings
from vimiv.utils import xdg


_files_directory = None
_info_directory = None


def init():
    """Create the necessary directories."""
    global _files_directory, _info_directory
    _files_directory = os.path.join(xdg.get_user_data_dir(), "Trash/files")
    _info_directory = os.path.join(xdg.get_user_data_dir(), "Trash/info")
    os.makedirs(_files_directory, exist_ok=True)
    os.makedirs(_info_directory, exist_ok=True)


class Signals(QObject):
    """Signals emitted after deleting and undeleting paths.

    Signals:
        path_removed: Emitted after delete to clear path from filelists.
            arg1: The path to remove from filelists.
        path_restored: Emitted after undelete to restore path to filelists.
            arg1: The path to restore to filelists.
    """

    path_removed = pyqtSignal(str)
    path_restored = pyqtSignal(str)


signals = Signals()


@keybindings.add("x", "delete %")
@commands.argument("filename")
@commands.register()
def delete(filename):
    """Move a file to the trash directory.

    **syntax:** ``:delete filename``

    positional arguments:
        * ``filename``: The name of the file to delete.
    """
    if not os.path.exists(filename):
        raise cmdexc.CommandError("path '%s' does not exist" % (filename))
    filename = os.path.abspath(filename)
    trash_filename = _get_trash_filename(filename)
    _create_info_file(trash_filename, filename)
    shutil.move(filename, trash_filename)
    signals.path_removed.emit(filename)


@commands.argument("basename")
@commands.register()
def undelete(basename):
    """Restore a file from the trash directory.

    **syntax:** ``:undelete basename``

    positional arguments:
        * ``basename``: The basename of the file in the trash directory.
    """
    trash_filename = os.path.join(_files_directory, basename)
    info_filename = _get_info_filename(basename)
    if not os.path.exists(info_filename) \
            or not os.path.exists(trash_filename):
        raise cmdexc.CommandError("file does not exist")
    original_filename, _ = get_trash_info(basename)
    if not os.path.isdir(os.path.dirname(original_filename)):
        raise cmdexc.CommandError("original directory is not accessible")
    shutil.move(trash_filename, original_filename)
    os.remove(info_filename)
    signals.path_restored.emit(original_filename)


def _get_trash_filename(filename):
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


def _get_info_filename(filename):
    basename = os.path.basename(filename)
    return os.path.join(_info_directory, basename + ".trashinfo")


def _create_info_file(trash_filename, original_filename):
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
    temp_file.write("Path=%s\n" % (original_filename))
    temp_file.write("DeletionDate=%s\n" % (time.strftime("%Y%m%dT%H%M%S")))
    # Make sure that all data is on disk
    temp_file.flush()
    os.fsync(temp_file.fileno())
    temp_file.close()
    shutil.move(temp_path, info_path)


def get_trash_info(filename):
    """Get information stored in the .trashinfo file.

    Args:
        filename: Name of the file to get info on.
    Return:
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
