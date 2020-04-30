# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.files."""

import imghdr
import os
import tarfile

from PyQt5.QtGui import QImageReader

import pytest

from vimiv.utils import files


SUPPORTED_IMAGE_FORMATS = ["jpg", "png", "gif", "svg", "cr2"]


@pytest.fixture()
def mockimghdr(mocker):
    """Fixture to mock imghdr.tests and QImageReader supportedImageFormats."""
    mocker.patch.object(
        QImageReader, "supportedImageFormats", return_value=SUPPORTED_IMAGE_FORMATS
    )
    yield mocker.patch("imghdr.tests", [])


@pytest.fixture()
def tmpfile(tmpdir):
    path = tmpdir.join("anything")
    path.write("")
    yield str(path)


def test_listdir_wrapper(mocker):
    mocker.patch("os.listdir", return_value=["a.txt", "b.txt"])
    mocker.patch("os.path.abspath", return_value="")
    assert files.listdir("directory") == ["a.txt", "b.txt"]


def test_listdir_wrapper_returns_abspath(mocker):
    dirname, paths = "dir", ["a.txt", "b.txt"]
    mocker.patch("os.listdir", return_value=paths)
    mocker.patch("os.path.abspath", return_value=dirname)
    expected = [os.path.join(dirname, path) for path in paths]
    assert files.listdir("directory") == expected


def test_listdir_wrapper_sort(mocker):
    mocker.patch("os.listdir", return_value=["b.txt", "a.txt"])
    mocker.patch("os.path.abspath", return_value="")
    assert files.listdir("directory") == ["a.txt", "b.txt"]


def test_listdir_wrapper_remove_hidden(mocker):
    mocker.patch("os.listdir", return_value=[".dotfile.txt", "a.txt"])
    mocker.patch("os.path.abspath", return_value="")
    assert files.listdir("directory") == ["a.txt"]


def test_listdir_wrapper_show_hidden(mocker):
    mocker.patch("os.listdir", return_value=[".dotfile.txt", "a.txt"])
    mocker.patch("os.path.abspath", return_value="")
    assert files.listdir("directory", show_hidden=True) == [".dotfile.txt", "a.txt"]


def test_directories_supported(mocker):
    mocker.patch("os.path.isdir", return_value=True)
    mocker.patch("os.path.isfile", return_value=False)
    images, directories = files.supported(["a", "b"])
    assert not images
    assert directories == ["a", "b"]


def test_images_supported(mocker):
    mocker.patch("os.path.isdir", return_value=False)
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("imghdr.what", return_value=True)
    images, directories = files.supported(["a", "b"])
    assert images == ["a", "b"]
    assert not directories


def test_tar_gz_not_an_image(tmpdir):
    """Test if is_image for a tar.gz returns False.

    The default implementation of QImageReader.canRead returns True which is not
    correct.
    """
    outfile = str(tmpdir.join("dummy.tar.gz"))
    indirectory = str(tmpdir.mkdir("indir"))
    with tarfile.open(outfile, mode="w:gz") as tar:
        tar.add(indirectory, arcname=os.path.basename(indirectory))
    assert files.is_image(outfile) is False


def test_is_image_on_error(tmpdir):
    path = tmpdir.join("my_file")
    path.write("")
    path.chmod(0o00)
    assert files.is_image(path) is False


def test_is_image_on_fifo_file(qtbot, tmpdir):
    path = tmpdir.join("my_file")
    os.mkfifo(path)
    assert files.is_image(path) is False


@pytest.mark.parametrize(
    "size, expected", [(510, "510B"), (2048, "2.0K"), (3 * 1024 ** 8, "3.0Y")]
)
def test_sizeof_fmt(size, expected):
    assert files.sizeof_fmt(size) == expected


def test_get_size_directory_with_directories(mocker):
    paths = [str(i) for i in range(15)]
    mocker.patch("os.listdir", return_value=paths)
    mocker.patch("os.path.isdir", return_value=True)
    mocker.patch("os.path.isfile", return_value=False)
    assert files.get_size_directory("any") == "15"


def test_get_size_directory_with_images(mocker):
    paths = [str(i) for i in range(10)]
    mocker.patch("os.listdir", return_value=paths)
    mocker.patch("os.path.isdir", return_value=False)
    mocker.patch.object(files, "is_image", return_value=True)
    assert files.get_size_directory("any") == "10"


def test_get_size_with_permission_error(mocker):
    mocker.patch("os.path.isfile", side_effect=PermissionError)
    assert files.get_size("any") == "N/A"


def test_listfiles(tmpdir):
    tmpdir.join("file0").open("w")  # File in root directory
    sub0 = tmpdir.mkdir("sub0")  # Sub-directory with two files
    sub0.join("file0").open("w")
    sub0.join("file1").open("w")
    tmpdir.mkdir("sub1").join("file0").open("w")  # Sub-directory with one file
    tmpdir.mkdir("sub2")  # Sub-directory with no files
    expected = [
        "file0",
        os.path.join("sub0", "file0"),
        os.path.join("sub0", "file1"),
        os.path.join("sub1", "file0"),
    ]
    assert sorted(expected) == sorted(files.listfiles(str(tmpdir)))


@pytest.mark.parametrize("name", SUPPORTED_IMAGE_FORMATS)
def test_add_supported_format(mockimghdr, tmpfile, name):
    files.add_image_format(name, _test_dummy)
    assert mockimghdr, "No test added by add image format"
    assert imghdr.what(tmpfile) == name


def test_add_unsupported_format(mockimghdr, tmpfile):
    files.add_image_format("not_a_format", _test_dummy)
    assert imghdr.what(tmpfile) is None
    assert not mockimghdr, "Unsupported test not removed"


def _test_dummy(h, f):
    """Dummy image file test that always returns True."""
    return True
