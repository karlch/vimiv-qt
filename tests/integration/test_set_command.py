# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.


import pytest

from vimiv.commands import cmdexc
from vimiv.config import settings, configcommands


def test_override_with_new_value(cleansetup):
    configcommands.set("library.width", "1234")
    assert settings.get_value("library.width") == 1234


def test_add_to_number_setting(cleansetup):
    before = settings.get_value("library.width")
    configcommands.set("library.width", "+20")
    assert settings.get_value("library.width") == before + 20


def test_toggle_bool_setting(cleansetup):
    before = settings.get_value("statusbar.show")
    configcommands.set("statusbar.show!")
    assert settings.get_value("statusbar.show") is not before


def test_fail_add_to_bool(cleansetup):
    with pytest.raises(cmdexc.CommandError):
        configcommands.set("statusbar.show", "+10")


def test_fail_unknown_setting(cleansetup):
    with pytest.raises(cmdexc.CommandError, match="unknown setting"):
        configcommands.set("not.a.setting", "+10")
