# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv.utils import objreg


bdd.scenarios("libraryscroll.feature")


@bdd.then(bdd.parsers.parse("the row should be {row}"))
def check_row_number(row):
    library = objreg.get("library")
    assert library.row() + 1 == int(row)
