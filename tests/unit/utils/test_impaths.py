# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.impaths."""

from unittest.mock import Mock

from vimiv.imutils import impaths


def test_load_paths_into_storage(cleansetup):
    mockfunc = Mock()
    impaths.signals.new_image.connect(mockfunc)
    impaths.load(["a", "b"])
    mockfunc.assert_called_once()


def test_get_abspath_of_current_image(cleansetup):
    impaths.load(["a/b", "b/c"])
