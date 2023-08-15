# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import io
import logging
import sys

import pytest_bdd as bdd

import vimiv
from vimiv.qt.core import QBuffer
from vimiv.qt.gui import QPixmap
from vimiv.utils import log


bdd.scenarios("startup.feature")


@bdd.given(bdd.parsers.parse("I patch stdin for {n_images:d} images"))
def patch_stdin(monkeypatch, tmp_path, n_images):
    paths = [tmp_path / f"image_{i:02d}.jpg\n" for i in range(1, n_images + 1)]
    stdin = io.StringIO("".join(str(path) for path in paths))
    monkeypatch.setattr(sys, "stdin", stdin)


@bdd.given(bdd.parsers.parse("I patch stdin for a binary image"))
def patch_binary_stdin(monkeypatch):
    buf = QBuffer()
    QPixmap(300, 300).save(buf, "jpg")

    stdin = io.StringIO()
    stdin.buffer = io.BytesIO(bytes(buf.data()))

    monkeypatch.setattr(sys, "stdin", stdin)


@bdd.then("the version information should be displayed")
def check_version_information(output):
    assert vimiv.__name__ in output.out
    assert vimiv.__version__ in output.out


@bdd.then(bdd.parsers.parse("the log level should be {level}"))
def check_log_level(level):
    loglevel = getattr(logging, level.upper())
    assert log._app_logger.level == loglevel
