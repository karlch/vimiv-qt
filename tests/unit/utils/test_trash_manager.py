# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.trash_manager."""

import os

import pytest

from vimiv.utils import trash_manager


def create_tmpfile(tmpdir, basename):
    """Simple function to create a temporary file using the tmpdir fixture."""
    path = tmpdir.join(basename)
    path.write("temporary")
    return str(path)


@pytest.fixture()
def tmpfile(tmpdir):
    """Create a temporary file as fixture using tmpdir."""
    yield create_tmpfile(tmpdir, "file")


@pytest.fixture()
def trash(monkeypatch, tmpdir):
    """Initialize trash for testing as fixture.

    Returns:
        The path to the temporary trash directory.
    """
    xdg_data_home = tmpdir.mkdir("data")
    monkeypatch.setenv("XDG_DATA_HOME", str(xdg_data_home))
    trash_manager.init()
    yield os.path.join(str(xdg_data_home), "Trash")


def test_delete_file(trash, tmpfile):
    trash_manager.delete(tmpfile)
    assert not os.path.exists(tmpfile)


def test_delete_and_undelete_file(trash, tmpfile):
    trash_manager.delete(tmpfile)
    basename = os.path.basename(tmpfile)
    trash_manager.undelete(basename)
    assert os.path.exists(tmpfile)


def test_do_not_override_existing_file_in_trash(trash, tmpdir):
    for i in range(2):
        path = create_tmpfile(tmpdir, "new_file")
        trash_manager.delete(path)
    trashdir = os.path.join(trash, "files")
    assert os.path.exists(os.path.join(trashdir, "new_file"))
    assert os.path.exists(os.path.join(trashdir, "new_file.2"))


def test_create_trash_info_file(trash, tmpdir):
    for i in range(2):
        path = create_tmpfile(tmpdir, "new_file")
        trash_manager.delete(path)
    infodir = os.path.join(trash, "info")
    assert os.path.exists(os.path.join(infodir, "new_file.trashinfo"))
    assert os.path.exists(os.path.join(infodir, "new_file.2.trashinfo"))
