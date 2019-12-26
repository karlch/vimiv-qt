# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to store and run commands."""

from typing import cast


def number_for_command(number: int = None, count: int = None, *, max_count: int) -> int:
    """Return correct number for command given number, optional count and a maximum.

    Count is preferred over the number if it is given. The command expects numbers
    indexed from one but returns a number indexed from zero. If the number exceeds the
    maximum, the modulo operator is used to reduce it accordingly.
    """
    if number is None and count is None:
        raise ValueError("Either number or count must be given")
    if count is not None:
        number = count
    number = cast(int, number)  # Ensured by the two tests above
    if number > 0:
        number -= 1
    return number % max_count
