# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Integration tests related to reading keybindings from configuration file."""

import pytest

from vimiv import api
from vimiv.config import keyfile


########################################################################################
#            Bindings dictionaries used to parametrize the keybinding file             #
########################################################################################
UPDATED_BINDINGS = {
    "GLOBAL": {"gh": "open ~"},
    "LIBRARY": {"<return>": "open-selected --close"},
}

REMOVE_J_BINDING = {"IMAGE": {"j": keyfile.DEL_BINDING_COMMAND}}


########################################################################################
#                                      Fixtures                                        #
########################################################################################
@pytest.fixture(autouse=True)
def reset_to_default(cleanup_helper):
    """Fixture to ensure everything is reset to default after testing."""
    yield from cleanup_helper(api.keybindings._registry)
    api.settings.reset()


@pytest.fixture(scope="function")
def keyspath(custom_configfile, request):
    """Fixture to create a custom keybindings file for reading."""
    yield custom_configfile(
        "keys.conf", keyfile.read, keyfile.get_default_parser, **request.param
    )


@pytest.fixture()
def bind_j():
    """Fixture to ensure j is bound to a command."""
    api.keybindings.bind("j", "scroll down", api.modes.IMAGE)


########################################################################################
#                                        Tests                                         #
########################################################################################
@pytest.mark.parametrize("keyspath", [UPDATED_BINDINGS], indirect=["keyspath"])
def test_read_bindings(keyspath):
    """Ensure keybindings are read correctly."""
    for modename, content in UPDATED_BINDINGS.items():
        mode = api.modes.get_by_name(modename.lower())
        for binding, command in content.items():
            modes = api.modes.GLOBALS if mode == api.modes.GLOBAL else (mode,)
            for mode in modes:
                assert api.keybindings._registry[mode][binding].value == command


@pytest.mark.parametrize("keyspath", [REMOVE_J_BINDING], indirect=["keyspath"])
def test_delete_binding(bind_j, keyspath):
    image_bindings = api.keybindings.get(api.modes.IMAGE)
    assert "j" not in image_bindings
