# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.trash_manager."""

import os

import pytest

from vimiv.utils import trash_manager, objreg


def create_tmpfile(tmpdir, basename):
    path = str(tmpdir.join(basename))
    with open(path, "w") as f:
        f.write("temporary")
    return path


@pytest.fixture()
def trash(tmpdir, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmpdir))
    trash_manager.init()
    path = create_tmpfile(tmpdir, "file")
    yield objreg.get("trash-manager"), path
    objreg.clear()


def test_delete_file(trash):
    manager, path = trash[0], trash[1]
    manager.delete(path)
    assert not os.path.exists(path)


def test_delete_and_undelete_file(trash):
    manager, path = trash[0], trash[1]
    manager.delete(path)
    basename = os.path.basename(path)
    manager.undelete(basename)
    assert os.path.exists(path)


def test_do_not_override_existing_file_in_trash(tmpdir, trash):
    manager = trash[0]
    for i in range(2):
        path = create_tmpfile(tmpdir, "new_file")
        manager.delete(path)
    trashdir = os.path.join(str(tmpdir), "Trash", "files")
    assert os.path.exists(os.path.join(trashdir, "new_file"))
    assert os.path.exists(os.path.join(trashdir, "new_file.2"))
