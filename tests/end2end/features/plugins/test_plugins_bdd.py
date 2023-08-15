# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd

from vimiv import plugins
from vimiv.utils import imageheader


bdd.scenarios("plugins.feature")


@bdd.when(bdd.parsers.parse("I load the {name} plugin with {info}"))
def load_plugin(name, info):
    plugins._load_plugin(name, info, plugins._app_plugin_directory)


@bdd.then(bdd.parsers.parse("The {name} format should be supported"))
def check_format_supported(name):
    assert name in [
        filetype for filetype, _ in imageheader._registry
    ], f"Image format {name} is not supported"
