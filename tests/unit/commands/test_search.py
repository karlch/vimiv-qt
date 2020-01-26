# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.search"""

from vimiv.commands import search


def test_clear_search():
    search.search._text = "Something"
    search.search.clear()
    assert search.search._text == ""


def test_sort_for_search():
    testlist = [1, 2, 3]
    updated_list = search._sort_for_search(testlist, 1, False)
    assert updated_list == [2, 3, 1]


def test_sort_for_search_reverse():
    testlist = [1, 2, 3]
    updated_list = search._sort_for_search(testlist, 1, True)
    assert updated_list == [2, 1, 3]
