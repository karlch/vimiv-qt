# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Initialize the classes to load and select image paths."""

from vimiv.imutils import imloader, imstorage, imfile_handler


def init():
    """Initialize the classes needed for imutils."""
    imstorage.Storage()
    imloader.ImageLoader()
    imfile_handler.ImageFileHandler()
