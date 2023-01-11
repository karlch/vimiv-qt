# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv import api, imutils


bdd.scenarios("imageorder.feature")


@bdd.then("the filelist should not be ordered")
def check_filelist_not_ordered():
    paths = imutils.pathlist()
    ordered_paths = api.settings.sort.image_order.sort(paths)
    assert paths != ordered_paths
