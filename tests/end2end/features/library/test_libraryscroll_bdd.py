# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2022 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import math

import pytest_bdd as bdd

from vimiv.utils import quotedjoin


bdd.scenarios("libraryscroll.feature")


@bdd.then(bdd.parsers.parse("the library should be {num} page {direction}"))
@bdd.then(bdd.parsers.parse("the library should be {num} pages {direction}"))
def check_library_page(library, num, direction):
    nums = {"one": 1, "half a": 0.5, "two": 2}
    assert num in nums, f"Invalid num '{num}'. Must be one of {quotedjoin(nums)}"
    multiplier = nums[num]
    pagesize = _get_pagesize(library)
    scrollstep = pagesize - 1
    expected_row = math.ceil(scrollstep * multiplier)
    row = library.row()
    assert row == expected_row


def _get_pagesize(library):
    """Simple implementation to get the library pagesize.

    Only works if there is no empty space in the viewport.
    """
    view_height = library.viewport().height()
    row_height = library.visualRect(library.model().index(1, 0)).height()
    n_rows = math.ceil(view_height / row_height)
    return n_rows
