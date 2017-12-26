# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Initialize the classes to load and select image paths."""

from vimiv.imutils import imloader, imstorage


def init():
    imstorage.Storage()
    imloader.ImageLoader()
