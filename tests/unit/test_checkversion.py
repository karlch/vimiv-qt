# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Unit tests for vimiv.checkversion."""

import sys

import pytest

from vimiv import checkversion
import vimiv.qt.core


@pytest.mark.parametrize("version_info", ((1,), (2, 6), (3, 5, 900)))
def test_check_python_version(capsys, monkeypatch, version_info):
    """Tests to ensure exit and error message on too low python version."""
    monkeypatch.setattr(sys, "version_info", version_info)

    with pytest.raises(SystemExit, match=str(checkversion.ERR_CODE)):
        checkversion.check_python_version()

    expected = build_message(
        "python", checkversion.PYTHON_REQUIRED_VERSION, version_info
    )
    captured = capsys.readouterr()
    assert captured.err == expected


@pytest.mark.parametrize("version_info", ((1,), (4, 6), (5, 8, 900)))
def test_check_pyqt_version(capsys, monkeypatch, version_info):
    """Tests to ensure exit and error message on too low PyQt version."""
    monkeypatch.setattr(
        vimiv.qt.core, "PYQT_VERSION_STR", ".".join(str(i) for i in version_info)
    )

    with pytest.raises(SystemExit, match=str(checkversion.ERR_CODE)):
        checkversion.check_pyqt_version()

    expected = build_message("PyQt", checkversion.PYQT_REQUIRED_VERSION, version_info)
    captured = capsys.readouterr()
    assert captured.err == expected


def build_message(software, required, version):
    """Helper to create the expected error message on too low software version."""
    # pylint: disable=consider-using-f-string
    return "At least %s %s is required to run vimiv. Using %s.\n" % (
        software,
        ".".join(str(i) for i in required),
        ".".join(str(i) for i in version),
    )
