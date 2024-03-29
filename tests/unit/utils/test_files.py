# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Tests for vimiv.utils.files."""

import collections
import os
import tarfile

import pytest

from vimiv.utils import files


@pytest.fixture()
def directory_tree(tmp_path):
    """Fixture to create a directory tree.

    Tree structure:
    .
    ├── file0
    ├── sub0
    │   ├── file0
    │   └── file1
    ├── sub1
    │   └── file0
    └── sub2
    """

    def create_subdirectory(*, index: int, n_children: int):
        subdirectory = tmp_path / f"sub{index:d}"
        subdirectory.mkdir()
        for i in range(n_children):
            subdirectory.joinpath(f"file{i:d}").touch()

    tmp_path.joinpath("file0").touch()  # File in root directory
    create_subdirectory(index=0, n_children=2)  # Directory with 2 files
    create_subdirectory(index=1, n_children=1)  # Directory with 1 file
    create_subdirectory(index=2, n_children=0)  # Directory with 0 files

    files = [
        "file0",
        os.path.join("sub0", "file0"),
        os.path.join("sub0", "file1"),
        os.path.join("sub1", "file0"),
    ]

    return collections.namedtuple("directorytree", ("root", "files"))(tmp_path, files)


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
    mocker.patch("vimiv.utils.imageheader.detect", return_value=True)
    images, directories = files.supported(["a", "b"])
    assert images == ["a", "b"]
    assert not directories


def test_tar_gz_not_an_image(tmp_path):
    """Test if is_image for a tar.gz returns False.

    The default implementation of QImageReader.canRead returns True which is not
    correct.
    """
    tarpath = tmp_path / "dummy.tar.gz"
    tarred_directory = tmp_path / "indir"
    tarred_directory.mkdir()
    with tarfile.open(tarpath, mode="w:gz") as tar:
        tar.add(tarred_directory, arcname=tarred_directory.name)
    assert files.is_image(str(tarpath)) is False


def test_is_image_on_error(tmp_path):
    path = tmp_path / "my_file"
    path.touch(mode=0o000)
    assert files.is_image(str(path)) is False


def test_is_image_on_fifo_file(qtbot, tmp_path):
    path = tmp_path / "my_file"
    os.mkfifo(path)
    assert files.is_image(str(path)) is False


@pytest.mark.parametrize(
    "size, expected", [(510, "510B"), (2048, "2.0K"), (3 * 1024**8, "3.0Y")]
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


def test_listfiles(directory_tree):
    expected = sorted(directory_tree.files)
    assert expected == sorted(files.listfiles(str(directory_tree.root)))
