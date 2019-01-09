# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils"""

from vimiv import utils


def test_ignore_single_exception():
    with utils.ignore(ValueError):
        int("32")


def test_ignore_multiple_exceptions():
    with utils.ignore(ValueError, IndexError):
        int("32")
        [][1]
