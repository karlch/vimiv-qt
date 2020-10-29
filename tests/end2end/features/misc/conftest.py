# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

from PyQt5.QtGui import QGuiApplication, QClipboard

import pytest
import pytest_bdd as bdd


@pytest.fixture()
def clipboard():
    return QGuiApplication.clipboard()


@bdd.then(bdd.parsers.parse("The clipboard should contain {text}"))
def check_clipboard(clipboard, text):
    assert text in clipboard.text(mode=QClipboard.Clipboard)


@bdd.then(bdd.parsers.parse("The primary selection should contain {text}"))
def check_primary(clipboard, text):
    assert text in clipboard.text(mode=QClipboard.Selection)
