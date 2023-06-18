# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import imghdr  # pylint: disable=deprecated-module

import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("imageopen.feature")


@bdd.when("I open broken images")
def open_broken_images(tmp_path):
    _open_file(tmp_path, b"\211PNG\r\n\032\n")  # PNG
    _open_file(tmp_path, b"000000JFIF")  # JPG
    _open_file(tmp_path, b"GIF89a")  # GIF
    _open_file(tmp_path, b"II")  # TIFF
    _open_file(tmp_path, b"BM")  # BMP


def _open_file(directory, data):
    """Open a file containing the bytes from data."""
    path = directory / "broken"
    path.write_bytes(data)
    filename = str(path)
    assert imghdr.what(filename) is not None, "Invalid magic bytes in test setup"
    api.open_paths([filename])
