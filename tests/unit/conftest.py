# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Fixtures for pytest unit tests."""

import pytest


@pytest.fixture()
def tmpfile(tmp_path):
    path = tmp_path / "anything"
    path.touch()
    yield str(path)
