# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Plugin enabling support for additional image formats.

Adds support for image formats that are not supported by Qt natively or by the
qtimageformats add-on, but instead require some other Qt module.

The required Qt module is not installed by Vimiv and requires explicit installation.

Activate it by adding::

    imageformats = name, ...

to the plugins section of your ``vimiv.conf``. Here name is the name of the format as
defined by QImageReader.supportedFormats() and as listed in the FORMATS dictionary.

To implement a new format::

    1) Implement the test function. It receives the first 32 bytes of the file as
       first argument and the open bytes file reader as second argument. Usually you
       will want to look for specific bytes in first argument. The function must
       return the boolean value indicating if the checked file is of this format or
       not.

    2) Extend the FORMATS dictionary with your format name as key and the test function
       as value. Note that the format name must be the one given by
       ``QImageReader.supportedImageFormats()``.
"""

from typing import Any, BinaryIO


from vimiv.utils import log, imageheader

_logger = log.module_logger(__name__)


def _test_cr2(h: bytes, _f: BinaryIO) -> bool:
    """Canon Raw 2 (CR2).

    Extension: .cr2

    Magic bytes:
    - 49 49 2A 00 10 00 00 00 43 52

    Support: QtRaw https://gitlab.com/mardy/qtraw
    """
    return h[:10] == b"\x49\x49\x2A\x00\x10\x00\x00\x00\x43\x52"


def _test_avif(h: bytes, _f: BinaryIO) -> bool:
    """AV1 Image File (AVIF).

    Extension: .avif

    Magic bytes:
    - ?

    Support: qt-qvif-image-plugin https://github.com/novomesk/qt-avif-image-plugin
    """
    return h[4:12] in (b"ftypavif", b"ftypavis")


FORMATS = {
    "cr2": _test_cr2,
    "avif": _test_avif,
}


def init(names: str, *_args: Any, **_kwargs: Any) -> None:
    """Initialize additional image formats.

    Args:
        names: Names separated by a comma of the image formats to add.
    """
    for name in names.split(","):
        name = name.lower().strip()
        try:
            check = FORMATS[name]
            # Set priority as these types are explicitly enables
            imageheader.register(name, check, priority=True)
            _logger.debug("Added image format '%s'", name)
        except KeyError:
            _logger.error("Ignoring unknown image format '%s'", name)
