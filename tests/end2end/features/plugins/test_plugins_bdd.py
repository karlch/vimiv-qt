# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd
from PyQt5.QtWidgets import QApplication

from vimiv import plugins


bdd.scenarios("plugins.feature")


@bdd.when(bdd.parsers.parse("I load the {name} plugin"))
def load_plugin(name):
    plugins.load(name)


@bdd.then("the print dialog should be displayed")
def check_print_dialog():
    print_dialog_window = _find_window("Print")
    assert print_dialog_window is not None, "Print dialog window not found"
    print_dialog_window.close()


@bdd.then("the print preview dialog should be displayed")
def check_print_preview_dialog():
    print_preview_window = _find_window("Print Preview")
    assert print_preview_window is not None, "Print preview dialog window not found"
    print_preview_window.close()


def _find_window(title):
    for window in QApplication.topLevelWindows():
        if window.title() == title:
            return window
    return None
