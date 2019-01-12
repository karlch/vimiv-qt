# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions dealing with files and paths."""

import datetime
import itertools
import os

from PyQt5.QtGui import QImageReader

from vimiv.config import settings
from vimiv.gui import statusbar
from vimiv.utils import pathreceiver


def ls(directory, show_hidden=False):  # pylint: disable=invalid-name
    """Wrapper around os.listdir.

    Args:
        directory: Directory to check for files in via os.listdir(directory).
        show_hidden: Include hidden files in output.
    Return:
        Sorted list of files in the directory with their absolute path.
    """
    directory = os.path.abspath(os.path.expanduser(directory))

    def listdir_wrapper(show_hidden):
        """Wrapper around os.listdir to possible hide dotfiles."""
        for path in os.listdir(directory):
            if not path.startswith(".") or show_hidden:
                yield os.path.join(directory, path)

    return sorted(listdir_wrapper(show_hidden))


def supported(paths):
    """Get a list of supported images and a list of directories from paths.

    Args:
        paths: List containing paths to parse.
    Return:
        images: List of images inside the directory.
        directories: List of directories inside the directory.
    """
    directories = []
    images = []
    for path in paths:
        if os.path.isdir(path):
            directories.append(path)
        elif is_image(path):
            images.append(path)
    return images, directories


def get_size(path):
    """Get the size of a path in human readable format.

    If the path is an image, the filesize is returned in the form of 2.3M. If
    the path is a directory, the amount of supported files in the directory is
    returned.

    Return:
        Size of path as string.
    """
    try:
        if os.path.isfile(path):
            return sizeof_fmt(os.path.getsize(path))
        return get_size_directory(path)
    except PermissionError:
        return "N/A"


def sizeof_fmt(num):
    """Print size of a byte number in human-readable format.

    Args:
        num: Filesize in bytes.

    Return:
        Filesize in human-readable format.
    """
    for unit in ["B", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            if abs(num) < 100:
                return "%3.1f%s" % (num, unit)
            return "%3.0f%s" % (num, unit)
        num /= 1024.0
    return "%.1f%s" % (num, "Y")


def yield_supported(paths):
    """Generator to yield supported paths.

    Args:
        paths: List of paths to check for supported paths.
    Return:
        Generator yielding paths if they are supported.
    """
    for path in paths:
        if os.path.isdir(path) or is_image(path):
            yield path


def get_size_directory(path):
    """Get size of directory by checking amount of supported paths.

    Args:
        path: Path to directory to check.
    Return:
        Size as formatted string.
    """
    max_amount = settings.get_value(settings.Names.LIBRARY_FILE_CHECK_AMOUNT)
    if max_amount == 0:  # Check all
        max_amount = None
    size = len(list(itertools.islice(yield_supported(ls(path)), max_amount)))
    if size == max_amount:
        return ">%d" % (max_amount)
    return str(size)


def is_image(filename):
    """Check whether a file is an image.

    Args:
        filename: Name of file to check.
    """
    if not os.path.isfile(filename):
        return False
    reader = QImageReader(filename)
    return reader.canRead()


def is_animation(filename):
    """Check whether a file is an animated image.

    Args:
        filename: Name of file to check.
    """
    raise NotImplementedError


def is_svg(filename):
    """Check whether a file is a vector graphic.

    Args:
        filename: Name of file to check.
    """
    raise NotImplementedError


def edit_supported(filename):
    """Check whether a file is editable for vimiv.

    Args:
        filename: Name of file to check.
    """
    raise NotImplementedError


@statusbar.module("{pwd}")
def pwd():
    """Current working directory."""
    wd = os.getcwd()
    if settings.get_value(settings.Names.STATUSBAR_COLLAPSE_HOME):
        wd = wd.replace(os.path.expanduser("~"), "~")
    return wd


@statusbar.module("{filesize}")
def filesize():
    """Size of the current image in bytes."""
    return get_size(pathreceiver.current())


@statusbar.module("{modified}")
def modified():
    """Modification date of the current image."""
    mtime = os.path.getmtime(pathreceiver.current())
    d = datetime.datetime.fromtimestamp(mtime)
    return d.strftime("%y-%m-%d %H:%M")


def open_paths(paths, select_mode=True):
    return True
