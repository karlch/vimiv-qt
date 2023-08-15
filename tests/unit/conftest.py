# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Fixtures for pytest unit tests."""

import pytest


@pytest.fixture()
def tmpfile(tmp_path):
    path = tmp_path / "anything"
    path.touch()
    yield str(path)
