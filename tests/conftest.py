# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Fixtures for pytest."""

import contextlib

import pytest

from PyQt5.QtGui import QPixmap, QImageWriter


@pytest.fixture
def tmpimage(tmpdir, qtbot):
    """Create an image to work with."""
    path = str(tmpdir.join("any_image.png"))
    width = 10
    height = 10
    pm = QPixmap(width, height)
    qtbot.addWidget(pm)
    writer = QImageWriter(path)
    assert writer.write(pm.toImage())
    return path


@pytest.fixture
def cleanup_helper():
    """Fixture to keep vimiv registries clean.

    Returns a contextmanager that resets the state of a dictionary to the initial state
    before running tests.
    """

    @contextlib.contextmanager
    def cleanup(init_dict):
        init_content = {key: dict(value) for key, value in init_dict.items()}
        yield
        new_content = {key: dict(value) for key, value in init_dict.items()}
        for key, valuedict in new_content.items():
            for elem in valuedict:
                if elem not in init_content[key]:
                    del init_dict[key][elem]

    return cleanup
