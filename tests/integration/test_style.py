# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.config.styles which require files."""

import os

import pytest

from vimiv.config import styles


def test_dump_and_read_default_style(mocker, tmpdir):
    # Create default
    styles.create_default()
    # Write to file
    confdir = str(tmpdir)
    tmpdir.mkdir("styles")
    mocker.patch("vimiv.utils.xdg.get_vimiv_config_dir", return_value=confdir)
    styles.dump("default")
    assert os.path.isfile(tmpdir.join("styles", "default"))
    # Clear to make sure the values did not just stay
    styles.clear()
    with pytest.raises(KeyError):
        styles.get("image.bg")
    styles.read("default")
    # Very simple assertion as default values can change
    assert "#" in styles.get("image.bg")
