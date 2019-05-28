# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest_bdd as bdd

from vimiv.imutils import filelist
from vimiv.gui import image
from vimiv.utils import working_directory


bdd.scenarios("imagedelete.feature")


@bdd.when("I wait for the working directory handler")
def wait_for_working_directory_handler(qtbot):
    with qtbot.waitSignal(working_directory.handler.changed):
        pass


@bdd.then(bdd.parsers.parse("{basename} should not be in the filelist"))
def check_image_not_in_filelist(basename):
    abspath = os.path.abspath(basename)
    assert abspath not in filelist._paths


@bdd.then("the image widget should be empty")
def check_image_widget_empty():
    assert isinstance(image.instance().widget(), image.Empty)
