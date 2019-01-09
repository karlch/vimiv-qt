# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Various utility functions."""

from contextlib import contextmanager


@contextmanager
def ignore(*exceptions):
    """Context manager to ignore given exceptions.

    Usage:
        with ignore(ValueError):
            int("hello")

    Behaves like:
        try:
            int("hello")
        except ValueError:
            pass
    """
    try:
        yield
    except exceptions:
        pass
