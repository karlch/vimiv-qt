# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd

from vimiv import api, imutils


bdd.scenarios("imageorder.feature")


@bdd.then("the filelist should not be ordered")
def check_filelist_not_ordered():
    paths = imutils.pathlist()
    ordered_paths = api.settings.sort.image_order.sort(paths)
    assert paths != ordered_paths
