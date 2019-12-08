# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Plugin enabling support for additional image formats.

Activate it by adding::

    imageformats = name, ...

to the plugins section of your ``vimiv.conf``. Here name is the name of the format as
defined by QImageReader.supportedFormats() and as listed in the FORMATS dictionary.
"""

from typing import Any, BinaryIO

from vimiv.utils import log, files

_logger = log.module_logger(__name__)


def test_cr2(header: bytes, _f: BinaryIO) -> bool:
    return header[:2] in (b"II", b"MM") and header[8:10] == b"CR"


FORMATS = {
    "cr2": test_cr2,
}


def init(names: str, *_args: Any, **_kwargs: Any) -> None:
    """Initialize additional image formats.

    Args:
        names: Names separated by a comma of the image formats to add.
    """
    for name in names.split(","):
        name = name.lower().strip()
        try:
            test = FORMATS[name]
            files.add_image_format(name, test)
            _logger.debug("Added image format '%s'", name)
        except KeyError:
            _logger.error("Ignoring unknown image format '%s'", name)
