# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv.parser import geometry
from vimiv.imutils import _ImageFileHandler


@pytest.fixture()
def file_handler():
    """Fixture to retrieve the current instance of the edit handler."""
    return _ImageFileHandler.instance


@pytest.fixture()
def edit_handler(file_handler):
    """Fixture to retrieve the current instance of the edit handler."""
    return file_handler._edit_handler


@bdd.then(bdd.parsers.parse("the image size should be {size}"))
def ensure_size(size, image):
    expected = geometry(size)
    image_rect = image.sceneRect()
    assert expected.width() == pytest.approx(image_rect.width(), abs=1)
    assert expected.height() == pytest.approx(image_rect.height(), abs=1)


@bdd.then(bdd.parsers.parse("the image size should not be {size}"))
def ensure_size_not(size, image):
    expected = geometry(size)
    image_rect = image.sceneRect()
    width_neq = expected.width() != image_rect.width()
    height_neq = expected.height() != image_rect.height()
    assert width_neq or height_neq


@bdd.then("the image should not be edited")
def ensure_not_edited(edit_handler):
    assert not edit_handler.changed
