# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.trash_manager."""

import collections
import os
import pathlib

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
    return paths(
        pathlib.Path(original_filename),
        pathlib.Path(trash_filename),
        pathlib.Path(info_filename),
    )


def test_delete_file(deleted_file):
    assert not deleted_file.original.exists(), "Original file not deleted"
    assert deleted_file.trash.exists(), "File not moved to trash"


def test_undelete_file(deleted_file):
    trash_manager.undelete(deleted_file.trash.name)
    assert deleted_file.original.exists(), "Original file not restored"
    assert not deleted_file.trash.exists(), "File not removed from trash"
    assert not deleted_file.info.exists(), "File info not removed from trash"


def test_create_trashinfo(deleted_file):
    with open(deleted_file.info, "r", encoding="utf-8") as f:
        content = f.read()

    assert content.startswith("[Trash Info]"), "Trash info header not created"
    assert f"Path={deleted_file.original}" in content, "Original path not written"
    assert "DeletionDate=" in content, "Deletion date not written"


def test_do_not_overwrite_trash_file(deleted_file):
    deleted_file.original.touch()
    trash_manager.delete(deleted_file.original)
    assert os.path.exists(str(deleted_file.trash) + ".2")
    assert os.path.exists(str(deleted_file.info).replace(".trashinfo", ".2.trashinfo"))


def test_fail_undelete_non_existing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="File for"):
        path = tmp_path / "any" / "random" / "file"
        trash_manager.undelete(str(path))


def test_fail_undelete_non_existing_original_directory(tmp_path):
    directory = tmp_path / "directory"
    directory.mkdir()
    original_filename = create_tmpfile(directory, "file")
    trash_filename = trash_manager.delete(original_filename)
    directory.rmdir()
    with pytest.raises(FileNotFoundError, match="Original directory"):
        trash_manager.undelete(pathlib.Path(trash_filename).name)


def test_undelete_symlink(tmp_path):
    path = tmp_path / "file"
    path.touch()
    path_to_link = tmp_path / "link"
    path_to_link.symlink_to("file")
    trash_filename = trash_manager.delete(str(path_to_link))
    trash_manager.undelete(trash_filename)
    assert path_to_link.exists()
    assert path_to_link.is_symlink()
    assert path_to_link.resolve() == path


def create_tmpfile(directory, basename):
    """Simple function to create a temporary file using pathlib."""
    path = directory / basename
    path.touch()
    return str(path)
