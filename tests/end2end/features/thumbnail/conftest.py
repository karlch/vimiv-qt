# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd


@bdd.then(bdd.parsers.parse("there should be {number:d} thumbnails"))
def check_thumbnail_amount(thumbnail, number):
    assert thumbnail.model().rowCount() == number
