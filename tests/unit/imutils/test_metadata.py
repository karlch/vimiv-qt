# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.metadata."""

import pytest

from vimiv.imutils import metadata


@pytest.fixture(
    params=[metadata.ExternalKeyHandler, metadata._ExternalKeyHandlerPiexif]
)
def external_handler(request):
    """Parametrized pytest fixture to yield the different external handlers."""
    yield request.param


def test_check_external_dependency():
    default = None
    assert metadata.check_external_dependancy(default) == default


def test_check_external_dependency_piexif(piexif):
    default = None
    assert (
        metadata.check_external_dependancy(default)
        == metadata._ExternalKeyHandlerPiexif
    )


def test_check_external_dependency_noexif(noexif):
    default = None
    assert (
        metadata.check_external_dependancy(default) == metadata._ExternalKeyHandlerBase
    )


@pytest.mark.parametrize(
    "methodname, args",
    (
        ("copy_metadata", ("dest.jpg",)),
        ("get_date_time", ()),
        ("fetch_key", ([],)),
        ("get_keys", ()),
    ),
)
def test_handler_base_raises(methodname, args):
    handler = metadata._ExternalKeyHandlerBase()
    method = getattr(handler, methodname)
    with pytest.raises(metadata.UnsupportedMetadataOperation):
        method(*args)


@pytest.mark.parametrize(
    "handler, expected_msg",
    (
        (metadata.ExternalKeyHandler, "not supported by pyexiv2"),
        (metadata._ExternalKeyHandlerPiexif, "not supported by piexif"),
        (metadata._ExternalKeyHandlerBase, "not supported. Please install"),
    ),
)
def test_handler_exception_customization(handler, expected_msg):
    with pytest.raises(metadata.UnsupportedMetadataOperation, match=expected_msg):
        handler.raise_exception("test operation")
