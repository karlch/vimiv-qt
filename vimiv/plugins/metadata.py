# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Metadata plugin wrapping the available backends to only load one."""

from vimiv.plugins import metadata_piexif, metadata_pyexiv2
from vimiv.utils import log

_logger = log.module_logger(__name__)


def init(*args, **kwargs):
    if metadata_pyexiv2.pyexiv2 is not None:
        metadata_pyexiv2.init()
    elif metadata_piexif.piexif is not None:
        metadata_piexif.init()
    else:
        _logger.warning("Please install either py3exiv2 or piexif for metadata support")
