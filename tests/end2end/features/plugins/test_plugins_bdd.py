# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import imghdr
from contextlib import suppress

import pytest_bdd as bdd

from vimiv import plugins


bdd.scenarios("plugins.feature")


@bdd.when(bdd.parsers.parse("I load the {name} plugin with {info}"))
def load_plugin(name, info):
    plugins._load_plugin(name, info, plugins._app_plugin_directory)


@bdd.then(bdd.parsers.parse("The {name} format should be supported"))
def check_format_supported(name):
    for func in imghdr.tests:
        with suppress(IndexError):
            format_name = func.__name__.split("_")[-1]
            if format_name == name:
                return
    assert False, f"Image format {name} is not supported"
