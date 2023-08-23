# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd

from vimiv import api
from vimiv.utils import imageheader


bdd.scenarios("imageopen.feature")


@bdd.when("I open broken images")
def open_broken_images(tmp_path):
    _open_file(tmp_path, b"\x89PNG\x0D\x0A\x1A\x0A")  # PNG
    _open_file(tmp_path, b"\xFF\xD8\xFF\xDB")  # JPG
    _open_file(tmp_path, b"GIF89a")  # GIF
    _open_file(tmp_path, b"II\x2A\x00")  # TIFF
    _open_file(tmp_path, b"BM")  # BMP


def _open_file(directory, data):
    """Open a file containing the bytes from data."""
    path = directory / "broken"
    path.write_bytes(data)
    filename = str(path)
    assert imageheader.detect(filename) is not None, "Invalid magic bytes in test setup"
    api.open_paths([filename])
