# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import imghdr

import pytest_bdd as bdd

from vimiv import app


bdd.scenarios("imageopen.feature")


@bdd.when("I open broken images")
def open_broken_images(tmpdir):
    _open_file(tmpdir, b"\211PNG\r\n\032\n")  # PNG
    _open_file(tmpdir, b"000000JFIF")  # JPG
    _open_file(tmpdir, b"GIF89a")  # GIF
    _open_file(tmpdir, b"II")  # TIFF
    _open_file(tmpdir, b"BM")  # BMP


def _open_file(tmpdir, data):
    """Open a file containing the bytes from data."""
    path = str(tmpdir.join("broken"))
    with open(path, "wb") as f:
        f.write(data)
    assert imghdr.what(path) is not None, "Invalid magic bytes in test setup"
    app.open([path])
