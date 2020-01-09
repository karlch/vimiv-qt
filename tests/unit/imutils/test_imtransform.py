# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.imtransform."""

from functools import partial
from unittest import mock

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

import pytest

from vimiv.imutils import imtransform


class MockHandler(mock.MagicMock):
    """Stub used as file handler for Transform.

    Provides a generic pixmap for all pixmaps and is always editable.
    """

    def __init__(self):
        super().__init__()
        self._pixmap = QPixmap(300, 300)
        self._pixmap.fill(Qt.black)

    @property
    def editable(self):
        return True

    @property
    def transformed(self):
        return self._pixmap

    @transformed.setter
    def transformed(self, value):
        pass

    original = current = transformed


ACTIONS = (
    imtransform.Transform.rotate_command,
    imtransform.Transform.flip,
    partial(imtransform.Transform.resize, width=400, height=400),
    partial(imtransform.Transform.rescale, dx=2, dy=2),
)


@pytest.fixture(scope="function")
def transform(qtbot):
    """Fixture to retrieve a clean Transform instance."""
    transform.handler = MockHandler()  # Keep as reference here due to weakref
    return imtransform.Transform(transform.handler)


@pytest.fixture(params=ACTIONS)
def action(transform, request):
    action = request.param
    return partial(action, self=transform)


def test_change_and_reset(action, transform):
    """Ensure every action leads to a change and is appropriately reset."""
    action()
    assert transform.changed
    transform.reset()
    assert not transform.changed
