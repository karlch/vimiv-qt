# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Tests for vimiv.version."""

import pytest

from vimiv import version


@pytest.fixture
def no_svg_support(monkeypatch):
    monkeypatch.setattr(version, "QtSvg", None)


def test_svg_support_info():
    assert "svg support: true" in version.info().lower()


def test_no_svg_support_info(no_svg_support):
    assert "svg support: false" in version.info().lower()
