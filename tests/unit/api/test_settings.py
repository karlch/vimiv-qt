# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.config.settings."""

import pytest

from vimiv.api import settings


def test_init_setting():
    b = settings.BoolSetting("bool", True)
    assert b.default
    assert b.value
    assert b.is_default()


def test_check_default_after_change_for_setting(mocker):
    b = settings.BoolSetting("bool", True)
    b.value = False
    assert not b.is_default()
    assert b.default


def test_set_bool_setting(mocker):
    b = settings.BoolSetting("bool", True)
    b.value = False
    assert not b.value


def test_set_bool_setting_str(mocker):
    b = settings.BoolSetting("bool", True)
    b.value = "False"
    assert not b.value


def test_toggle_bool_setting():
    b = settings.BoolSetting("bool", False)
    b.toggle()
    assert b.value


def test_set_int_setting(mocker):
    i = settings.IntSetting("int", 1)
    i.value = 2
    assert i.value == 2


def test_set_int_setting_str(mocker):
    i = settings.IntSetting("int", 1)
    i.value = "2"
    assert i.value == 2


def test_add_int_setting(mocker):
    i = settings.IntSetting("int", 2)
    i += 3
    assert i.value == 5


def test_multiply_int_setting(mocker):
    i = settings.IntSetting("int", 5)
    i *= 2
    assert i.value == 10


def test_set_float_setting(mocker):
    f = settings.FloatSetting("float", 2.2)
    f.value = 3.3
    assert f.value == pytest.approx(3.3)


def test_set_float_setting_str(mocker):
    f = settings.FloatSetting("float", 2.2)
    f.value = "3.3"
    assert f.value == pytest.approx(3.3)


def test_add_float_setting(mocker):
    f = settings.FloatSetting("float", 1.1)
    f += 0.3
    assert f.value == pytest.approx(1.4)


def test_multiply_float_setting(mocker):
    f = settings.FloatSetting("float", 4.2)
    f *= 0.5
    assert f.value == pytest.approx(2.1)


def test_set_thumbnail_setting(mocker):
    t = settings.ThumbnailSizeSetting("thumb", 128)
    t.value = 64
    assert t.value == 64


def test_set_thumbnail_setting_str(mocker):
    t = settings.ThumbnailSizeSetting("thumb", 128)
    t.value = "64"
    assert t.value == 64


def test_fail_set_thumbnail_setting_non_int(mocker):
    t = settings.ThumbnailSizeSetting("thumb", 128)
    with pytest.raises(ValueError, match="Cannot convert 'any'"):
        t.value = "any"


def test_fail_set_thumbnail_setting_wrong_int(mocker):
    t = settings.ThumbnailSizeSetting("thumb", 128)
    with pytest.raises(ValueError, match="must be one of"):
        t.value = 13


def test_increase_thumbnail_size():
    t = settings.ThumbnailSizeSetting("thumb", 128)
    t.increase()
    assert t.value == 256


def test_increase_thumbnail_size_at_limit():
    t = settings.ThumbnailSizeSetting("thumb", 512)
    t.increase()
    assert t.value == 512


def test_decrease_thumbnail_size():
    t = settings.ThumbnailSizeSetting("thumb", 128)
    t.decrease()
    assert t.value == 64


def test_decrease_thumbnail_size_at_limit():
    t = settings.ThumbnailSizeSetting("thumb", 64)
    t.decrease()
    assert t.value == 64


def test_set_str_setting():
    s = settings.StrSetting("string", "default")
    s.value = "new"
    assert s.value == "new"


def test_fail_set_str_setting():
    s = settings.StrSetting("string", "default")
    with pytest.raises(ValueError, match="can only convert String"):
        s.value = 12


def test_fail_get_unstored_setting():
    with pytest.raises(KeyError):
        settings.get("any")
