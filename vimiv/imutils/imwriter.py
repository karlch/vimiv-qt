# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Functions to write an image to disk."""

import os

from PyQt5.QtGui import QPixmap, QImageReader

from vimiv.commands import commands, cmdexc
from vimiv.imutils import imstorage, imloader


@commands.argument("path", optional=True)
@commands.register(mode="image")
def write(path):
    """Write an image to disk.

    Args:
        path: Use path instead of currently loaded path.
    """
    path = path if path else imstorage.current()
    image = imloader.current()
    _can_write(path, image)
    image.save(path)
    if not os.path.isfile(path):
        _, ext = os.path.splitext(path)
        raise cmdexc.CommandError(
            "Writing '%s' failed. Is '%s' a valid image extension?"
            % (path, ext))


def _can_write(path, image):
    """Check if the given path is writable.

    Raises CommandError if writing is not possible.

    Args:
        path: Path to write to.
        image: QPixmap to write.
    """
    # Writing animations is not supported
    if not isinstance(image, QPixmap):
        raise cmdexc.CommandError("Cannot write animations")
    # Override current path
    elif os.path.exists(path):
        reader = QImageReader(path)
        if not reader.canRead():
            raise cmdexc.CommandError(
                "Path '%s' exists and is not an image" % (path))
