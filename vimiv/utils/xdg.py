# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to help with XDG_USER_* settings."""

import os


def get_user_data_dir():
    return os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))


def get_user_config_dir():
    return os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))


def get_user_cache_dir():
    return os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))


def get_vimiv_data_dir():
    return os.path.join(get_user_data_dir(), "vimiv")


def get_vimiv_cache_dir():
    return os.path.join(get_user_cache_dir(), "vimiv")


def get_vimiv_config_dir():
    return os.path.join(get_user_config_dir(), "vimiv")


def join_vimiv_data(path):
    return os.path.join(get_vimiv_data_dir(), path)


def join_vimiv_cache(path):
    return os.path.join(get_vimiv_cache_dir(), path)


def join_vimiv_config(path):
    return os.path.join(get_vimiv_config_dir(), path)
