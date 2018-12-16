# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.search"""

from vimiv.commands import search


def test_clear_search(mocker):
    mocker.patch("vimiv.utils.objreg")
    search_class = search.Search()
    search_class._text = "Something"
    search_class.clear()
    assert search_class._text == ""


def test_sort_for_search(mocker):
    mocker.patch("vimiv.utils.objreg")
    search_class = search.Search()
    testlist = [1, 2, 3]
    updated_list = search_class._sort_for_search(testlist, 1, False)
    assert updated_list == [3, 1, 2]


def test_sort_for_search_reverse(mocker):
    mocker.patch("vimiv.utils.objreg")
    search_class = search.Search()
    testlist = [1, 2, 3]
    updated_list = search_class._sort_for_search(testlist, 1, True)
    assert updated_list == [1, 3, 2]


def test_get_next_match(mocker):
    mocker.patch("vimiv.utils.objreg")
    mocker.patch("vimiv.config.settings.get_value", return_value=True)
    search_class = search.Search()
    testlist = ["one", "two", "three"]
    next_match, matches = search_class._get_next_match("t", 1, testlist)
    assert next_match == "two"
    assert matches == ["two", "three"]


def test_get_no_match(mocker):
    mocker.patch("vimiv.utils.objreg")
    mocker.patch("vimiv.config.settings.get_value", return_value=True)
    search_class = search.Search()
    testlist = ["one", "two", "three"]
    next_match, matches = search_class._get_next_match("nothing", 1, testlist)
    # Returns the last element in the list as this is the starting point
    assert next_match == "three"
    assert matches == []
