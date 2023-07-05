# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.metadata."""

import pytest

from vimiv.imutils import metadata
from vimiv.plugins import metadata_piexif, metadata_pyexiv2


@pytest.fixture(autouse=True)
def reset_to_default(cleanup_helper):
    """Fixture to ensure everything is reset to default after testing."""
    registry = list(metadata._registry)
    yield
    metadata._registry = registry


@pytest.fixture
def nometadata():
    metadata._registry = []


@pytest.fixture
def piexif():
    metadata._registry = []
    metadata_piexif.init()


@pytest.fixture
def pyexiv2():
    metadata._registry = []
    metadata_pyexiv2.init()


@pytest.mark.parametrize(
    "methodname, args",
    (
        ("copy_metadata", ("dest.jpg",)),
        ("get_date_time", ()),
        ("get_metadata", ([],)),
        ("get_keys", ()),
    ),
)
def test_handler_raises(nometadata, methodname, args):
    assert not metadata.has_metadata_support()

    handler = metadata.MetadataHandler("path")
    method = getattr(handler, methodname)
    with pytest.raises(metadata.MetadataError):
        method(*args)


def test_piexif_initializes(piexif):
    assert metadata_piexif.MetadataPiexif in metadata._registry
    assert metadata.has_metadata_support()


def test_pyexiv2_initializes(pyexiv2):
    assert metadata_pyexiv2.MetadataPyexiv2 in metadata._registry
    assert metadata.has_metadata_support()
