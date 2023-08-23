# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("thumbnailzoom.feature")


@bdd.then(bdd.parsers.parse("the thumbnail size should be {size:d}"))
def check_thumbnail_size(thumbnail, size):
    # Check setting
    assert api.settings.thumbnail.size.value == size
    # Check actual value
    assert thumbnail.iconSize().width() == size
