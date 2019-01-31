# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to help with XDG_USER_* settings."""

import os


def user_data_dir() -> str:
    return os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))


def user_config_dir() -> str:
    return os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))


def user_cache_dir() -> str:
    return os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))


def vimiv_data_dir() -> str:
    return os.path.join(user_data_dir(), "vimiv")


def vimiv_cache_dir() -> str:
    return os.path.join(user_cache_dir(), "vimiv")


def vimiv_config_dir() -> str:
    return os.path.join(user_config_dir(), "vimiv")


def join_vimiv_data(*paths) -> str:
    return os.path.join(vimiv_data_dir(), *paths)


def join_vimiv_cache(*paths) -> str:
    return os.path.join(vimiv_cache_dir(), *paths)


def join_vimiv_config(*paths) -> str:
    return os.path.join(vimiv_config_dir(), *paths)
