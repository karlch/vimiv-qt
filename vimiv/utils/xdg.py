# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to help with XDG_USER_* settings."""

import os

from PyQt5.QtCore import QStandardPaths

import vimiv


basedir = None


def _standardpath(
    location: QStandardPaths.StandardLocation, name: str, *paths: str
) -> str:
    """Return absolute path to a standard storage directory.

    Args:
        location: Location ID according to QStandardPaths.
        name: Fallback name to use in case there is a base directory.
        paths: Any additional paths passed to os.path.join.
    """
    if basedir is not None:
        return os.path.join(basedir, name, *paths)
    return os.path.join(QStandardPaths.writableLocation(location), *paths)


def makedirs(*paths: str) -> None:
    for path in paths:
        os.makedirs(path, mode=0o700, exist_ok=True)


def user_data_dir(*paths: str) -> str:
    return _standardpath(QStandardPaths.GenericDataLocation, "data", *paths)


def user_config_dir(*paths: str) -> str:
    return _standardpath(QStandardPaths.GenericConfigLocation, "config", *paths)


def user_cache_dir(*paths: str) -> str:
    return _standardpath(QStandardPaths.GenericCacheLocation, "cache", *paths)


def vimiv_data_dir(*paths: str) -> str:
    return user_data_dir(vimiv.__name__, *paths)


def vimiv_cache_dir(*paths: str) -> str:
    return user_cache_dir(vimiv.__name__, *paths)


def vimiv_config_dir(*paths: str) -> str:
    return user_config_dir(vimiv.__name__, *paths)
