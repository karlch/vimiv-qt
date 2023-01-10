# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.version."""

import pytest

from vimiv import version
from vimiv.imutils import metadata


@pytest.fixture
def no_svg_support(monkeypatch):
    monkeypatch.setattr(version, "QtSvg", None)


def test_svg_support_info():
    assert "svg support: true" in version.info().lower()


def test_no_svg_support_info(no_svg_support):
    assert "svg support: false" in version.info().lower()


@pytest.mark.pyexiv2
def test_pyexiv2_info(pyexiv2):
    assert f"pyexiv2: {metadata._registry[0]('').version}" in version.info().lower()


@pytest.mark.piexif
def test_piexif_info(piexif):
    assert f"piexif: {metadata._registry[0]('').version}" in version.info().lower()


@pytest.mark.nometadata
def test_no_metadata_support_info(no_metadata_support):
    assert "metadata support: false" in version.info().lower()
