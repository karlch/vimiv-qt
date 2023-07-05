# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Metadata plugin wrapping the available backends to only load one."""

from typing import Any

from vimiv.plugins import metadata_piexif, metadata_pyexiv2
from vimiv.utils import log
from vimiv.imutils import metadata

_logger = log.module_logger(__name__)


def init(info: str, *_args: Any, **_kwargs: Any) -> None:
    """Initialize metadata plugin depending on available backend.

    If any other backend has already been registered, do not register any new one.
    """
    if metadata.has_metadata_support():
        _logger.debug(
            "Not loading a default metadata backend, as one has been loaded manually"
        )
    elif info.lower() == "none":
        _logger.debug("Not auto-loading metadata support as per user-request")
    elif metadata_pyexiv2.pyexiv2 is not None:
        _logger.debug("Auto-loading pyexiv2 metadata plugin")
        metadata_pyexiv2.init()
    elif metadata_piexif.piexif is not None:
        _logger.debug("Auto-loading piexif metadata plugin")
        metadata_piexif.init()
    else:
        _logger.warning(
            "Please install either py3exiv2 or piexif for metadata support.<br>\n"
            "For more information see<br>\n"
            "https://karlch.github.io/vimiv-qt/documentation/metadata.html",
        )
