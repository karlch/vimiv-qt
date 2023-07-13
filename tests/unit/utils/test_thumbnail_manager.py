# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import hashlib
import os

from PyQt5.QtGui import QPixmap

import pytest

from vimiv.api import settings
from vimiv.utils import thumbnail_manager


@pytest.fixture
def manager(qtbot, tmp_path, mocker):
    """Fixture to create a thumbnail manager with relevant methods mocked."""
    # Mock directory in which the thumbnails are created
    tmp_cache_dir = tmp_path / "cache"
    mocker.patch("vimiv.utils.xdg.user_cache_dir", return_value=str(tmp_cache_dir))
    # Create thumbnail manager and yield the instance
    yield thumbnail_manager.ThumbnailManager(None)


def test_thumbnail_save_disabled(monkeypatch, qtbot, tmp_path, manager):
    monkeypatch.setattr(settings.thumbnail.save, "value", False)
    no_thumbnail_path = str(tmp_path / "no_thumbnail.jpg")
    QPixmap(300, 300).save(no_thumbnail_path, "jpg")
    manager.create_thumbnails_async([0], [no_thumbnail_path])
    check_thumbails_created(qtbot, manager, 0)


def test_thumbnail_save_disabled_no_delete_old(monkeypatch, qtbot, tmp_path, manager):
    monkeypatch.setattr(settings.thumbnail.save, "value", True)
    has_thumbnail_path = str(tmp_path / "has_thumbnail.jpg")
    QPixmap(300, 300).save(has_thumbnail_path, "jpg")
    manager.create_thumbnails_async([0], [has_thumbnail_path])
    check_thumbails_created(qtbot, manager, 1)

    monkeypatch.setattr(settings.thumbnail.save, "value", False)
    no_thumbnail_path = str(tmp_path / "no_thumbnail.jpg")
    QPixmap(300, 300).save(no_thumbnail_path, "jpg")
    manager.create_thumbnails_async([0, 1], [has_thumbnail_path, no_thumbnail_path])
    check_thumbails_created(qtbot, manager, 1)


@pytest.mark.parametrize("n_paths", (1, 5))
def test_create_n_thumbnails(qtbot, tmp_path, manager, n_paths):
    # Create images to create thumbnails of
    filenames = [str(tmp_path / f"image_{i}.jpg") for i in range(n_paths)]
    for filename in filenames:
        QPixmap(300, 300).save(filename, "jpg")
    manager.create_thumbnails_async(range(0, len(filenames)), filenames)
    check_thumbails_created(qtbot, manager, n_paths)


def test_create_thumbnails_for_non_existing_path(qtbot, manager):
    manager.create_thumbnails_async([0], ["this/is/not/a/path"])
    check_thumbails_created(qtbot, manager, 0)


def test_create_thumbnails_for_non_image_path(qtbot, tmp_path, manager):
    filename = str(tmp_path / "image.jpg")
    manager.create_thumbnails_async([0], [filename])
    check_thumbails_created(qtbot, manager, 0)


def test_do_not_create_thumbnail_for_thumbnail(qtbot, manager):
    filename = os.path.join(
        manager.directory, hashlib.md5(b"thumbnail").hexdigest() + ".png"
    )
    QPixmap(256, 256).save(filename)
    manager.create_thumbnails_async([0], [filename])
    check_thumbails_created(qtbot, manager, 1)


def check_thumbails_created(qtbot, manager, n_paths):
    def wait_thread():
        assert manager.pool.activeThreadCount() == 0

    qtbot.waitUntil(wait_thread, timeout=30000)
    assert len(os.listdir(manager.directory)) == n_paths
