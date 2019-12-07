# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
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


########################################################################################
#                                      Fixtures                                        #
########################################################################################
@pytest.fixture(autouse=True)
def reset_to_default(cleanup_helper):
    """Fixture to ensure everything is reset to default after testing."""
    yield from cleanup_helper(
        api.keybindings._registry, keyupdate=api.keybindings._BindingsTrie.keysequence
    )
    api.settings.reset()


@pytest.fixture(scope="function")
def keyspath(tmpdir, custom_configfile, request):
    """Fixture to create a custom keybindings file for reading."""
    yield custom_configfile(
        "keys.conf", keyfile.read, keyfile.get_default_parser, **request.param
    )


########################################################################################
#                                        Tests                                         #
########################################################################################
@pytest.mark.parametrize("keyspath", [UPDATED_BINDINGS], indirect=["keyspath"])
def test_read_bindings(keyspath):
    """Ensure keybindings are read correctly."""
    for modename, content in UPDATED_BINDINGS.items():
        mode = api.modes.get_by_name(modename.lower())
        for binding, command in content.items():
            keysequence = api.keybindings._BindingsTrie.keysequence(binding)
            modes = api.modes.GLOBALS if mode == api.modes.GLOBAL else (mode,)
            for mode in modes:
                assert api.keybindings._registry[mode][keysequence].value == command
