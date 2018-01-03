# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.aliases."""

import pytest

from vimiv.commands import aliases
from vimiv.utils import objreg

@pytest.fixture
def setup():
    aliases.init()
    yield
    objreg.delete("aliases")


def test_add_alias(setup):
    aliases.alias("test", ["quit"])
    assert aliases.get("global")["test"] == "quit"


def test_fail_add_alias_no_list(setup):
    with pytest.raises(AssertionError, match="defined as list"):
        aliases.alias("test", "any")


def test_add_alias_for_different_mode(setup):
    aliases.alias("test", ["quit"], mode="image")
    assert aliases.get("image")["test"] == "quit"
    assert "test" not in aliases.get("global")


def test_get_global_alias_from_image_mode(setup):
    assert "q" in aliases.get("image")
