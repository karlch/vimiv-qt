# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest_bdd as bdd

from vimiv.qt.gui import QClipboard


bdd.scenarios("clipboard.feature")


@bdd.then(
    bdd.parsers.parse(
        # Need a slightly different wording so it cannot overlap with the previous
        # versions
        "the absolute path of {text} should be saved in the clipboard"
    )
)
def check_clipboard_abspath(clipboard, text):
    text = os.path.abspath(text)
    assert clipboard.text(mode=QClipboard.Clipboard) == text
