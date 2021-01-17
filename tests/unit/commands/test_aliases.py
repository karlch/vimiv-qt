# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.aliases."""

from typing import NamedTuple

import pytest

from vimiv import api
from vimiv.commands import aliases


class AliasDefinition(NamedTuple):
    name: str = "test"
    command: str = "quit"
    mode: api.modes.Mode = api.modes.GLOBAL


@pytest.fixture(params=[api.modes.GLOBAL])
def alias(request):
    """Pytest fixture to create and delete an alias.

    Default mode for alias creation is GLOBAL. This can be changed via indirect fixture
    parametrization.
    """
    mode = request.param
    definition = AliasDefinition(mode=mode)
    aliases.alias(definition.name, [definition.command], mode=definition.mode.name)
    yield definition
    del aliases._aliases[definition.mode][definition.name]


def test_add_global_alias(alias):
    """Ensure alias added for global mode is available in all global modes."""
    for mode in (*api.modes.GLOBALS, api.modes.GLOBAL):
        assert aliases.get(mode)[alias.name] == alias.command


@pytest.mark.parametrize("alias", api.modes.GLOBALS, indirect=True)
def test_add_local_alias(alias):
    """Ensure alias added for a single mode is only available in this mode."""
    assert aliases.get(alias.mode)[alias.name] == alias.command
    other = set(api.modes.ALL) - {alias.mode}
    for mode in other:
        with pytest.raises(KeyError, match=alias.name):
            aliases.get(mode)[alias.name]  # pylint: disable=expression-not-assigned


def test_fail_add_alias_no_list():
    with pytest.raises(AssertionError, match="defined as list"):
        aliases.alias("test", "any")


def test_fail_mode_not_as_str():
    with pytest.raises(AssertionError, match="Mode must be passed"):
        aliases.alias("test", ["any"], mode=api.modes.GLOBAL)
