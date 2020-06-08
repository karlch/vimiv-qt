# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.trash_manager."""

import collections
import os

import pytest

from vimiv.utils import trash_manager


@pytest.fixture(autouse=True)
def trash(monkeypatch, tmp_path):
    """Initialize trash for testing as fixture.

    Returns:
        The path to the temporary trash directory.
    """
    xdg_data_home = tmp_path / "data"
    monkeypatch.setenv("XDG_DATA_HOME", str(xdg_data_home))
    trash_manager.init()
    yield
    trash_manager.trash_info.cache_clear()


@pytest.fixture()
def deleted_file(tmp_path):
    original_filename = create_tmpfile(tmp_path, "file")
    trash_filename = trash_manager.delete(original_filename)
    info_filename = trash_manager._get_info_filename(original_filename)
    paths = collections.namedtuple("DeletedFile", ("original", "trash", "info"))
    return paths(original_filename, trash_filename, info_filename)


def test_delete_file(deleted_file):
    assert not os.path.exists(deleted_file.original), "Original file not deleted"
    assert os.path.exists(deleted_file.trash), "File not moved to trash"


def test_undelete_file(deleted_file):
    trash_basename = os.path.basename(deleted_file.trash)
    trash_manager.undelete(trash_basename)
    assert os.path.exists(deleted_file.original), "Original file not restored"
    assert not os.path.exists(deleted_file.trash), "File not removed from trash"
    assert not os.path.exists(deleted_file.info), "File info not removed from trash"


def test_create_trashinfo(deleted_file):
    with open(deleted_file.info, "r") as f:
        content = f.read()

    assert content.startswith("[Trash Info]"), "Trash info header not created"
    assert f"Path={deleted_file.original}" in content, "Original path not written"
    assert "DeletionDate=" in content, "Deletion date not written"


def test_do_not_overwrite_trash_file(deleted_file):
    with open(deleted_file.original, "w") as f:
        f.write("temporary")
    trash_manager.delete(deleted_file.original)
    assert os.path.exists(deleted_file.trash + ".2")
    assert os.path.exists(deleted_file.info.replace(".trashinfo", ".2.trashinfo"))


def test_fail_undelete_non_existing_file():
    with pytest.raises(FileNotFoundError, match="File for"):
        trash_manager.undelete(os.path.join("any", "random", "file"))


def test_fail_undelete_non_existing_original_directory(tmp_path):
    directory = tmp_path / "directory"
    directory.mkdir()
    original_filename = create_tmpfile(directory, "file")
    trash_filename = trash_manager.delete(original_filename)
    os.rmdir(directory)
    with pytest.raises(FileNotFoundError, match="Original directory"):
        trash_manager.undelete(os.path.basename(trash_filename))


def create_tmpfile(directory, basename):
    """Simple function to create a temporary file using pathlib."""
    path = directory / basename
    path.touch()
    return str(path)
