# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Dummy module used for testing the lazy import mechanism."""

print(__name__)  # Side effect we can check for

RETURN_VALUE = 42


def function_of_interest():
    return RETURN_VALUE
