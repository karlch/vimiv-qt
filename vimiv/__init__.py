# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""An image viewer with vim-like keybindings based on PyQt5."""

from . import checkversion, version

__license__ = "GPL3"
__version_info__ = (0, 4, 1)
__version__ = ".".join(str(num) for num in __version_info__)
__author__ = "Christian Karl"
__maintainer__ = __author__
__email__ = "karlch@protonmail.com"
__description__ = "An image viewer with vim-like keybindings."
__url__ = "https://karlch.github.io/vimiv-qt/"
