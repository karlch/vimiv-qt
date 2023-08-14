# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv.qt.gui import QGuiApplication, QClipboard


@pytest.fixture()
def clipboard():
    return QGuiApplication.clipboard()


@bdd.then(bdd.parsers.parse("The clipboard should contain '{text}'"))
def check_clipboard(clipboard, text):
    assert text in clipboard.text(mode=QClipboard.Mode.Clipboard)


@bdd.then(bdd.parsers.parse("The primary selection should contain '{text}'"))
def check_primary(clipboard, text):
    assert text in clipboard.text(mode=QClipboard.Mode.Selection)


@bdd.then(bdd.parsers.parse("The clipboard should contain any image"))
def check_clipboard_image(clipboard, image):
    assert not clipboard.pixmap(mode=QClipboard.Mode.Clipboard).toImage().isNull()


@bdd.then(bdd.parsers.parse("The primary selection should contain any image"))
def check_primary_image(clipboard, image):
    assert not clipboard.pixmap(mode=QClipboard.Mode.Selection).toImage().isNull()


@bdd.then(bdd.parsers.parse("The clipboard should contain an image with width {width}"))
def check_clipboard_image_width(clipboard, width):
    assert clipboard.pixmap(mode=QClipboard.Mode.Clipboard).size().width() == int(width)


@bdd.then(
    bdd.parsers.parse("The clipboard should contain an image with height {height}")
)
def check_clipboard_image_height(clipboard, height):
    assert clipboard.pixmap(mode=QClipboard.Mode.Clipboard).size().height() == int(
        height
    )


@bdd.then(bdd.parsers.parse("The clipboard should contain an image with size {size}"))
def check_clipboard_image_size(clipboard, size):
    assert max(
        clipboard.pixmap(mode=QClipboard.Mode.Clipboard).size().height(),
        clipboard.pixmap(mode=QClipboard.Mode.Clipboard).size().width(),
    ) == int(size)
