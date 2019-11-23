# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions dealing with files and paths."""

import imghdr
import os
from typing import List, Tuple, Optional, BinaryIO, Iterable

# We need the check as svg support is optional
try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None


def listdir(directory: str, show_hidden: bool = False) -> List[str]:
    """Wrapper around os.listdir.

    Args:
        directory: Directory to check for files in via os.listdir(directory).
        show_hidden: Include hidden files in output.
    Returns:
        Sorted list of files in the directory with their absolute path.
    """
    directory = os.path.abspath(os.path.expanduser(directory))
    return sorted(
        os.path.join(directory, path)
        for path in os.listdir(directory)
        if show_hidden or not path.startswith(".")
    )


def supported(paths: Iterable[str]) -> Tuple[List[str], List[str]]:
    """Get a list of supported images and a list of directories from paths.

    Args:
        paths: List containing paths to parse.
    Returns:
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

    Returns:
        Size of path as string.
    """
    try:
        isfile = os.path.isfile(path)
    except OSError:
        return "N/A"
    if isfile:
        return get_size_file(path)
    return get_size_directory(path)


def get_size_file(path: str) -> str:
    """Retrieve the size of a file as formatted byte number in human-readable format."""
    try:
        return sizeof_fmt(os.path.getsize(path))
    except OSError:
        return "N/A"


def sizeof_fmt(num: float) -> str:
    """Retrieve size of a byte number in human-readable format.

    Args:
        num: Filesize in bytes.

    Returns:
        Filesize in human-readable format.
    """
    for unit in ("B", "K", "M", "G", "T", "P", "E", "Z"):
        if num < 1024.0:
            if num < 100:
                return f"{num:3.1f}{unit}"
            return f"{num:3.0f}{unit}"
        num /= 1024.0
    return f"{num:.1f}Y"


def get_size_directory(path: str) -> str:
    """Get size of directory by checking amount of supported paths.

    Args:
        path: Path to directory to check.
    Returns:
        Size as formatted string.
    """
    try:
        return str(len(os.listdir(path)))
    except OSError:
        return "N/A"


def is_image(filename: str) -> bool:
    """Check whether a file is an image.

    Args:
        filename: Name of file to check.
    """
    try:
        return imghdr.what(filename) is not None
    except OSError:
        return False


def listfiles(directory: str, abspath: bool = False) -> List[str]:
    """Return list of all files in directory traversing the directory recursively.

    Args:
        directory: The directory to traverse.
        abspath: Return the absolute path to the files, not relative to directory.
    """
    return [
        os.path.join(root, fname)
        if abspath
        else os.path.join(root.replace(directory, "").lstrip("/"), fname)
        for root, _, files in os.walk(directory)
        for fname in files
    ]


# Only add svg check to imghdr if svg available
if QSvgWidget is not None:

    def _test_svg(first_bytes: bytes, _reader: BinaryIO) -> Optional[str]:
        """Check if an opened file is a svg.

        Appended to imghdr.tests to detect vector graphics.
        """
        return "svg" if _svg_encoding in first_bytes else None

    _svg_encoding = "<?xml".encode("utf-8")
    imghdr.tests.append(_test_svg)
