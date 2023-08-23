# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd

from vimiv.imutils import filelist


bdd.scenarios("imagetitle.feature")


@bdd.then("the image name should be in the window title")
def image_name_in_title(mainwindow):
    assert filelist.basename() in mainwindow.windowTitle()
