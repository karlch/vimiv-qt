# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Functions dealing with files and paths."""

import os

from PyQt5.QtGui import QImageReader

from vimiv.config import settings
from vimiv.gui import statusbar


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
        for path in os.listdir(directory):
            if not path.startswith(".") or show_hidden:
                yield os.path.join(directory, path)
    paths = listdir_wrapper(show_hidden)
    return sorted(paths)


def get_supported(paths):
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
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            directories.append(path)
        elif is_image(path):
            images.append(path)
    return images, directories


def is_image(filename):
    """Check whether a file is an image.

    Args:
        filename: Name of file to check.
    """
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
    """Print current working directory for the statusbar."""
    wd = os.getcwd()
    if settings.get_value("statusbar.collapse_home"):
        wd = wd.replace(os.path.expanduser("~"), "~")
    return wd
