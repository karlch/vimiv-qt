# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Fixtures for pytest."""

import pytest

from PyQt5.QtGui import QPixmap, QImageWriter

from vimiv.utils import objreg


@pytest.fixture
def tmpimage(tmpdir, qtbot):
    """Create an image to work with."""
    path = str(tmpdir.join("foo.png"))
    width = 10
    height = 10
    pm = QPixmap(width, height)
    qtbot.addWidget(pm)
    writer = QImageWriter(path)
    assert writer.write(pm.toImage())
    return path


@pytest.fixture
def objregistry():
    """Clear registry automatically."""
    yield objreg
    objreg.clear()
