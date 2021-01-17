# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd


@bdd.then(bdd.parsers.parse("there should be {number:d} thumbnails"))
def check_thumbnail_amount(thumbnail, number):
    assert thumbnail.model().rowCount() == number
