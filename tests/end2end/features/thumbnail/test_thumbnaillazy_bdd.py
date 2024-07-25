# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd


bdd.scenarios("thumbnaillazy.feature")


def wait_for_thumbnails_to_load(qtbot, thumbnail):
    def wait_thread():
        assert thumbnail._manager.pool.activeThreadCount() == 0

    qtbot.waitUntil(wait_thread, timeout=30000)


@bdd.then(bdd.parsers.parse("there should be {number:d} rendered thumbnails"))
def check_rendered_thumbnail_amount(qtbot, thumbnail, number):
    wait_for_thumbnails_to_load(qtbot, thumbnail)
    assert len(thumbnail._rendered_paths) == number


@bdd.then(bdd.parsers.parse("the last index should be {number:d}"))
def check_last_index(qtbot, thumbnail, number):
    wait_for_thumbnails_to_load(qtbot, thumbnail)
    assert thumbnail._last_rendered_index() == number


@bdd.then(bdd.parsers.parse("the first index should be {number:d}"))
def check_first_index(qtbot, thumbnail, number):
    wait_for_thumbnails_to_load(qtbot, thumbnail)
    assert thumbnail._first_rendered_index() == number


@bdd.then(bdd.parsers.parse("thumbnails should load in order of closeness to selected"))
def check_thumbnail_pair_order(qtbot, thumbnail):
    wait_for_thumbnails_to_load(qtbot, thumbnail)
    pairs = thumbnail._rendered_thumbnail_pairs()
    current_index = thumbnail.current_index()
    last_difference = -1
    for i, p in pairs.items():
        difference = abs(i - current_index)
        assert difference >= last_difference
        last_difference = difference
        assert p == thumbnail._paths[i]
