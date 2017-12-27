# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.config.settings."""

import pytest

from vimiv.config import settings
from vimiv.utils import strconvert


def test_init_setting():
    b = settings.BoolSetting("bool", True)
    assert b.get_default()
    assert b.get_value()
    assert b.is_default()


def test_check_default_after_change_for_setting(mocker):
    b = settings.BoolSetting("bool", True)
    mocker.patch.object(strconvert, "to_bool", return_value=False)
    b.override("false")
    strconvert.to_bool.assert_called_with("false")
    assert not b.is_default()
    assert b.get_default()


def test_override_bool_setting(mocker):
    b = settings.BoolSetting("bool", True)
    mocker.patch.object(strconvert, "to_bool", return_value=False)
    b.override("false")
    strconvert.to_bool.assert_called_with("false")
    assert not b.get_value()


def test_toggle_bool_setting():
    b = settings.BoolSetting("bool", False)
    b.toggle()
    assert b.get_value()


def test_override_int_setting(mocker):
    i = settings.IntSetting("int", 1)
    mocker.patch("vimiv.utils.strconvert.to_int", return_value=2)
    i.override("any")
    assert i.get_value() == 2


def test_add_int_setting(mocker):
    i = settings.IntSetting("int", 2)
    mocker.patch.object(strconvert, "to_int", return_value=3)
    i.add("any")
    assert i.get_value() == 5


def test_multiply_int_setting(mocker):
    i = settings.IntSetting("int", 5)
    mocker.patch.object(strconvert, "to_int", return_value=2)
    i.multiply("any")
    assert i.get_value() == 10


def test_override_float_setting(mocker):
    f = settings.FloatSetting("float", 2.2)
    mocker.patch.object(strconvert, "to_float", return_value=3.3)
    f.override("any")
    assert f.get_value() == pytest.approx(3.3)


def test_add_float_setting(mocker):
    f = settings.FloatSetting("float", 1.1)
    mocker.patch.object(strconvert, "to_float", return_value=0.3)
    f.add("any")
    assert f.get_value() == pytest.approx(1.4)


def test_multiply_float_setting(mocker):
    f = settings.FloatSetting("float", 4.2)
    mocker.patch.object(strconvert, "to_float", return_value=0.5)
    f.multiply("any")
    assert f.get_value() == pytest.approx(2.1)


def test_override_thumbnail_setting(mocker):
    t = settings.ThumbnailSizeSetting("thumb", 128)
    mocker.patch.object(strconvert, "to_int", return_value=64)
    t.override("any")
    assert t.get_value() == 64


def test_fail_override_thumbnail_setting(mocker):
    t = settings.ThumbnailSizeSetting("thumb", 128)
    mocker.patch.object(strconvert, "to_int", return_value=13)
    with pytest.raises(ValueError, match="must be one of"):
        t.override("any")


def test_increase_thumbnail_size():
    t = settings.ThumbnailSizeSetting("thumb", 128)
    t.increase()
    assert t.get_value() == 256


def test_increase_thumbnail_size_at_limit():
    t = settings.ThumbnailSizeSetting("thumb", 512)
    t.increase()
    assert t.get_value() == 512


def test_decrease_thumbnail_size():
    t = settings.ThumbnailSizeSetting("thumb", 128)
    t.decrease()
    assert t.get_value() == 64


def test_decrease_thumbnail_size_at_limit():
    t = settings.ThumbnailSizeSetting("thumb", 64)
    t.decrease()
    assert t.get_value() == 64


def test_override_str_setting():
    s = settings.StrSetting("string", "default")
    s.override("new")
    assert s.get_value() == "new"


def test_fail_override_str_setting():
    s = settings.StrSetting("string", "default")
    with pytest.raises(AssertionError, match="must be str"):
        s.override(12)


def test_fail_get_unstored_setting():
    with pytest.raises(KeyError):
        settings.get("any")
