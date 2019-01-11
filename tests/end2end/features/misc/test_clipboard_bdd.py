# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

from PyQt5.QtGui import QGuiApplication, QClipboard

import pytest
import pytest_bdd as bdd


bdd.scenarios("clipboard.feature")


@pytest.fixture()
def clipboard():
    yield QGuiApplication.clipboard()


@bdd.then(bdd.parsers.parse("The clipboard should be set to {text}"))
def check_clipboard(clipboard, text):
    assert clipboard.text(mode=QClipboard.Clipboard) == text


@bdd.then(bdd.parsers.parse("The primary selection should be set to {text}"))
def check_primary(clipboard, text):
    assert clipboard.text(mode=QClipboard.Selection) == text


@bdd.then(bdd.parsers.parse(
    # Need a slightly different wording so it cannot overlap with the previous
    # versions
    "the absolute path of {text} should be saved in the clipboard"))
def check_clipboard_abspath(clipboard, text):
    text = os.path.abspath(text)
    assert clipboard.text(mode=QClipboard.Clipboard) == text
