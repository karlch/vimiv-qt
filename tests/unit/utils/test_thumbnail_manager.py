# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os
import time

import pytest

from PyQt5.QtGui import QPixmap

from vimiv.utils import thumbnail_manager


@pytest.fixture
def manager(qtbot, tmpdir, mocker, monkeypatch):
    """Fixture to create a thumbnail manager with relevant methods mocked."""
    # Mock directory in which the thumbnails are created
    tmp_cache_dir = tmpdir.join("cache")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_cache_dir))
    # Create thumbnail manager and yield the instance
    # fail_pixmap = QPixmap(256, 256)
    instance = thumbnail_manager.ThumbnailManager(None)
    instance.created = mocker.Mock()
    yield instance
    # Cleanup
    monkeypatch.delenv("XDG_CACHE_HOME")


@pytest.mark.parametrize("n_paths", (1, 5))
def test_create_n_thumbnails(tmpdir, manager, n_paths):
    # Create images to create thumbnails of
    paths = [str(tmpdir.join(f"image_{i}.jpg")) for i in range(n_paths)]
    for path in paths:
        QPixmap(300, 300).save(path, "jpg")
    manager.create_thumbnails_async(paths)
    check_thumbails_created(manager, n_paths)


def test_create_thumbnails_for_non_existing_path(manager):
    manager.create_thumbnails_async(["this/is/not/a/path"])
    check_thumbails_created(manager, 0)


def test_create_thumbnails_for_non_image_path(tmpdir, manager):
    path = str(tmpdir.join("image.jpg"))
    manager.create_thumbnails_async([path])
    check_thumbails_created(manager, 0)


def check_thumbails_created(manager, n_paths):
    while manager.pool.activeThreadCount():
        time.sleep(0.001)
    assert len(os.listdir(manager.directory)) == n_paths
