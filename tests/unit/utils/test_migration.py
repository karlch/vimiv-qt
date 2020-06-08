# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.migration."""

import os

import pytest

from vimiv.utils import migration, xdg


TAGFILE_NAME = "tagfile"


@pytest.fixture
def mock_gtk_version(tmp_path, monkeypatch):
    """Fixture to mock the xdg directories and fill them with gtk-version-like files."""
    for name in ("cache", "config", "data"):
        directory = tmp_path / name
        directory.mkdir()
        monkeypatch.setenv(f"XDG_{name.upper()}_HOME", str(directory))

    for directory in (
        xdg.vimiv_config_dir(),
        xdg.vimiv_cache_dir(),
        xdg.vimiv_data_dir(),
    ):
        assert "home" not in directory, "patching the xdg directories failed"
        os.makedirs(directory)

    for basename in ("vimivrc", "keys.conf"):
        abspath = xdg.vimiv_config_dir(basename)
        with open(abspath, "w") as f:
            f.write("option: value\n")

    tag_dir = xdg.vimiv_data_dir("Tags")
    os.mkdir(tag_dir)
    tag_file = os.path.join(tag_dir, TAGFILE_NAME)
    with open(tag_file, "w") as f:
        for i in range(10):
            f.write(f"test_{i:02d}.jpg\n")

    yield
    migration.WelcomePopUp.gtk_installed = False


@pytest.fixture
def mock_backup(mocker):
    """Fixture to mock the backup functions."""
    mocker.patch.object(migration, "backup")
    mocker.patch.object(migration, "migrate_tags")
    yield


def test_run(mock_gtk_version, mock_backup):
    migration.run()
    migration.backup.assert_called_once()  # pylint: disable=no-member
    migration.migrate_tags.assert_called_once()  # pylint: disable=no-member
    assert migration.WelcomePopUp.gtk_installed


def test_do_not_run(mocker, mock_backup):
    mocker.patch.object(migration, "gtk_version_installed", return_value=False)
    migration.run()
    migration.backup.assert_not_called()  # pylint: disable=no-member
    assert not migration.WelcomePopUp.gtk_installed


def test_backup_directories(mock_gtk_version):
    migration.backup()
    gtk_name = "vimiv-gtk-backup"
    for directory in (
        xdg.user_config_dir(gtk_name),
        xdg.user_cache_dir(gtk_name),
        xdg.user_data_dir(gtk_name),
    ):
        assert os.path.isdir(directory)


def test_migrate_tags(mock_gtk_version):
    migration.migrate_tags(xdg.vimiv_data_dir())
    assert os.path.isdir(xdg.vimiv_data_dir("tags"))
    assert os.path.isfile(xdg.vimiv_data_dir("tags", TAGFILE_NAME))
