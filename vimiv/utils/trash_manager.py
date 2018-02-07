# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""Provides class to handle a shared trash directory.

The TrashManager deletes and undeletes images from the user's Trash directory
in $XDG_DATA_HOME/Trash according to the freedesktop.org trash specification.
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
from vimiv.utils import objreg, xdg


def init():
    """Create the TrashManager object."""
    TrashManager()


class TrashManager(QObject):
    """Provides mechanism to delete and undelete images.

    Attributes:
        files_directory: Directory to which the "deleted" files are moved.
        info_directory: Directory in which information on the trashed files is
        stored.

    Signals:
        path_removed: Emitted after delete to clear path from filelists.
            arg1: The path to remove from filelists.
        path_restored: Emitted after undelete to restore path to filelists.
            arg1: The path to restore to filelists.
    """

    path_removed = pyqtSignal(str)
    path_restored = pyqtSignal(str)

    @objreg.register("trash-manager")
    def __init__(self):
        """Create a new TrashManager."""
        super().__init__()
        self.files_directory = os.path.join(xdg.get_user_data_dir(),
                                            "Trash/files")
        self.info_directory = os.path.join(xdg.get_user_data_dir(),
                                           "Trash/info")
        os.makedirs(self.files_directory, exist_ok=True)
        os.makedirs(self.info_directory, exist_ok=True)

    @keybindings.add("x", "delete %")
    @commands.argument("filename")
    @commands.register(instance="trash-manager")
    def delete(self, filename):
        """Move a file to the trash directory.

        **syntax:** ``:delete filename``

        positional arguments:
            * ``filename``: The name of the file to delete.
        """
        if not os.path.exists(filename):
            raise cmdexc.CommandError("path '%s' does not exist" % (filename))
        filename = os.path.abspath(filename)
        trash_filename = self._get_trash_filename(filename)
        self._create_info_file(trash_filename, filename)
        shutil.move(filename, trash_filename)
        self.path_removed.emit(filename)

    @commands.argument("basename")
    @commands.register(instance="trash-manager")
    def undelete(self, basename):
        """Restore a file from the trash directory.

        **syntax:** ``:undelete basename``

        positional arguments:
            * ``basename``: The basename of the file in the trash directory.
        """
        trash_filename = os.path.join(self.files_directory, basename)
        info_filename = self._get_info_filename(basename)
        if not os.path.exists(info_filename) \
                or not os.path.exists(trash_filename):
            raise cmdexc.CommandError("file does not exist")
        original_filename, _ = self.get_trash_info(basename)
        if os.path.isdir(trash_filename):
            raise cmdexc.CommandError("directories are not supported")
        # Directory of the file is not accessible
        if not os.path.isdir(os.path.dirname(original_filename)):
            raise cmdexc.CommandError("original directory is not accessible")
        shutil.move(trash_filename, original_filename)
        os.remove(info_filename)
        self.path_restored.emit(original_filename)

    def _get_trash_filename(self, filename):
        """Return the name of the file in self.files_directory.

        Args:
            filename: The original name of the file.
        """
        path = os.path.join(self.files_directory, os.path.basename(filename))
        # Ensure that we do not overwrite any files
        extension = 2
        original_path = path
        while os.path.exists(path):
            path = original_path + "." + str(extension)
            extension += 1
        return path

    def _get_info_filename(self, filename):
        basename = os.path.basename(filename)
        return os.path.join(self.info_directory, basename + ".trashinfo")

    def _create_info_file(self, trash_filename, original_filename):
        """Create file with information as specified by the standard.

        Args:
            trash_filename: The name of the file in self.files_directory.
            original_filename: The original name of the file.
        """
        # Note: we cannot use configparser here as it writes keys in lowercase
        info_path = self._get_info_filename(trash_filename)
        # Write to temporary file and use shutil.move to make sure the
        # operation is an atomic operation as specified by the standard
        fd, temp_path = tempfile.mkstemp(dir=self.info_directory)
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

    def get_trash_info(self, filename):
        """Get information stored in the .trashinfo file.

        Args:
            filename: Name of the file to get info on.
        Return:
            original_filename: The absolute path to the original file.
            deletion_date: The deletion date.
        """
        info_filename = self._get_info_filename(filename)
        info = configparser.ConfigParser()
        info.read(info_filename)
        content = info["Trash Info"]
        original_filename = content["Path"]
        deletion_date = content["DeletionDate"]
        return original_filename, deletion_date
