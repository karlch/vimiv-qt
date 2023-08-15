# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd


bdd.scenarios("thumbnailmark.feature")


@bdd.then(bdd.parsers.parse("the thumbnail number {number:d} should be marked"))
def check_thumbnail_marked(thumbnail, number):
    item = thumbnail.item(number - 1)
    assert item is not None and item.marked
