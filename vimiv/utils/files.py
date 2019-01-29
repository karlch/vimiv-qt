# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions dealing with files and paths."""

import datetime
import itertools
import os
from typing import Generator, List, Tuple

from PyQt5.QtGui import QImageReader

from vimiv import api
from vimiv.utils import pathreceiver


def listdir(directory: str, show_hidden: bool = False) -> List[str]:
    """Wrapper around os.listdir.

    Args:
        directory: Directory to check for files in via os.listdir(directory).
        show_hidden: Include hidden files in output.
    Return:
        Sorted list of files in the directory with their absolute path.
    """
    directory = os.path.abspath(os.path.expanduser(directory))
    return sorted(
        os.path.join(directory, path)
        for path in os.listdir(directory)
        if show_hidden or not path.startswith(".")
    )


def supported(paths: List[str]) -> Tuple[List[str], List[str]]:
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


def get_size(path: str) -> str:
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


def sizeof_fmt(num: float) -> str:
    """Retrieve size of a byte number in human-readable format.

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


def yield_supported(paths: List[str]) -> Generator[str, None, None]:
    """Generator to yield supported paths.

    Args:
        paths: List of paths to check for supported paths.
    Return:
        Generator yielding paths if they are supported.
    """
    for path in paths:
        if os.path.isdir(path) or is_image(path):
            yield path


def get_size_directory(path: str) -> str:
    """Get size of directory by checking amount of supported paths.

    Args:
        path: Path to directory to check.
    Return:
        Size as formatted string.
    """
    max_amount = api.settings.LIBRARY_FILE_CHECK_AMOUNT.value
    if max_amount == 0:  # Check all
        max_amount = None
    size = len(list(itertools.islice(yield_supported(listdir(path)), max_amount)))
    if size == max_amount:
        return ">%d" % (max_amount)
    return str(size)


def is_image(filename: str) -> bool:
    """Check whether a file is an image.

    Args:
        filename: Name of file to check.
    """
    if not os.path.isfile(filename):
        return False
    reader = QImageReader(filename)
    return reader.canRead()


@api.status.module("{pwd}")
def pwd() -> str:
    """Current working directory."""
    wd = os.getcwd()
    if api.settings.STATUSBAR_COLLAPSE_HOME.value:
        wd = wd.replace(os.path.expanduser("~"), "~")
    return wd


@api.status.module("{filesize}")
def filesize() -> str:
    """Size of the current image in bytes."""
    return get_size(pathreceiver.current())


@api.status.module("{modified}")
def modified() -> str:
    """Modification date of the current image."""
    mtime = os.path.getmtime(pathreceiver.current())
    d = datetime.datetime.fromtimestamp(mtime)
    return d.strftime("%y-%m-%d %H:%M")
