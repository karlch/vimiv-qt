# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv import api
from vimiv.commands import search


bdd.scenarios("search.feature")


class SearchResults:
    """Helper class to store search results."""

    def __init__(self):
        self.results = []
        search.search.new_search.connect(self._on_search)
        search.search.cleared.connect(self._on_search_cleared)

    def _on_search(self, _index, results, _mode, _incsearch):
        self.results = results

    def _on_search_cleared(self):
        self.results.clear()

    def __len__(self):
        return len(self.results)


@pytest.fixture(autouse=True)
def search_results():
    """Fixture to retrieve a clean helper class to store search results."""
    return SearchResults()


@bdd.when(bdd.parsers.parse("I search for {text}"))
def run_search(text):
    search.search(text, api.modes.current())


@bdd.when(bdd.parsers.parse("I search in reverse for {text}"))
def run_search_reverse(text):
    search.search(text, api.modes.current(), reverse=True)


@bdd.then(bdd.parsers.parse("There should be {n:d} search matches"))
def check_search_matches(search_results, n):
    assert len(search_results) == n
