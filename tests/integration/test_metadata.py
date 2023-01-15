# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.imutils.metadata."""

import pytest

from vimiv.imutils import metadata


@pytest.mark.parametrize(
    "methodname, args",
    (
        ("copy_metadata", ("dest.jpg",)),
        ("get_date_time", ()),
        ("get_metadata", ([],)),
        ("get_keys", ()),
    ),
)
def test_handler_raises(methodname, args):
    assert not metadata.has_metadata_support()

    handler = metadata.MetadataHandler("path")
    method = getattr(handler, methodname)
    with pytest.raises(metadata.UnsupportedMetadataOperation):
        method(*args)
