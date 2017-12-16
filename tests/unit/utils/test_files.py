# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.utils.files."""

import os
from contextlib import ContextDecorator
from unittest.mock import MagicMock

from PyQt5.QtGui import QImageReader

from vimiv.utils import files


class mock_for_ls(ContextDecorator):  # pylint: disable=invalid-name
    """ContextDecorator to mock the functions called by files.ls.

    os.listdir returns whatever is passed to the constructor.
    os.abspath returns the same path as was passed as argument.

    This is not written as simple fixture as the expected return value of
    os.listdir is passed as argument.
    """

    def __init__(self, retval):
        """Store original functions and the expected return value."""
        super().__init__()
        self.old_listdir = os.listdir
        self.old_abspath = os.path.abspath
        self.retval = retval

    def __enter__(self):
        """Mock os.listdir and os.path.abspath."""
        os.listdir = MagicMock(return_value=self.retval)
        os.path.abspath = MagicMock(return_value="")
        return self

    def __exit__(self, *args):
        """Restore os.listdir and os.path.abspath."""
        os.listdir = self.old_listdir
        os.path.abspath = self.old_abspath


@mock_for_ls(["a.txt", "b.txt"])
def test_listdir_wrapper():
    assert files.ls("directory") == ["a.txt", "b.txt"]


@mock_for_ls(["file.txt", "other.txt", "a.txt"])
def test_listdir_wrapper_sort():
    assert files.ls("directory") == ["a.txt", "file.txt", "other.txt"]


@mock_for_ls(["file.txt", ".dotfile.txt"])
def test_listdir_wrapper_remove_hidden():
    assert files.ls("directory") == ["file.txt"]


@mock_for_ls([".dotfile.txt", "file.txt"])
def test_listdir_wrapper_show_hidden():
    assert files.ls("directory", show_hidden=True) \
        == [".dotfile.txt", "file.txt"]


class mock_for_get_supported(ContextDecorator):  # pylint: disable=invalid-name
    """ContextDecorator to mock the functions called by files.get_supported.

    files.ls always returns ["a", "b"].
    Either ospath.isdir or files.is_image return True, the other returns False.
    """

    def __init__(self, isdir):
        """Store original functions.

        Args:
            isdir: Treat all paths as directories, else as images.
        """
        self.isdir = isdir
        self.old_isdir = os.path.isdir
        self.old_is_image = files.is_image

    def __enter__(self):
        """Mock the functions."""
        os.path.isdir = MagicMock(return_value=self.isdir)
        files.is_image = MagicMock(return_value=not self.isdir)
        return self

    def __exit__(self, *args):
        """Restore old functions."""
        os.path.isdir = self.old_isdir
        files.is_image = self.old_is_image


@mock_for_get_supported(isdir=True)
def test_directories_supported():
    images, directories = files.get_supported(["a", "b"])
    assert not images
    assert directories == ["a", "b"]


@mock_for_get_supported(isdir=False)
def test_images_supported():
    images, directories = files.get_supported(["a", "b"])
    assert images == ["a", "b"]
    assert not directories


def test_is_image():
    QImageReader.canRead = MagicMock(return_value=True)
    assert files.is_image("any")


def test_is_not_image():
    QImageReader.canRead = MagicMock(return_value=False)
    assert not files.is_image("any")
