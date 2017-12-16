# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Test code interacting with the settings storage in vimiv.config.settings."""

import pytest

from vimiv.config import settings


# Initialize defaults
settings.init_defaults()


def test_has_settings_stored():
    assert settings.get_value("statusbar.show") is not None


def test_override_setting_in_storage():
    settings.override("statusbar.show", "no")
    assert not settings.get_value("statusbar.show")


def test_toggle_setting_in_storage():
    before = settings.get_value("statusbar.show")
    settings.toggle("statusbar.show")
    assert before != settings.get_value("statusbar.show")


def test_fail_toggle_non_bool_setting():
    with pytest.raises(TypeError, match="not store a bool"):
        settings.toggle("library.width")


def test_add_to_setting_in_storage():
    start = settings.get_value("library.width")
    settings.add_to("library.width", "200")
    assert settings.get_value("library.width") == start + 200


def test_fail_add_to_non_number_setting():
    with pytest.raises(TypeError, match="does not store a number"):
        settings.add_to("statusbar.show", "12")


def test_multiply_with_setting_in_storage():
    start = settings.get_value("library.width")
    settings.multiply_with("library.width", "2")
    assert settings.get_value("library.width") == pytest.approx(start * 2)


def test_fail_multiply_with_non_number_setting():
    with pytest.raises(TypeError, match="does not store a number"):
        settings.multiply_with("statusbar.show", "12")


def test_reset_storage_to_default():
    assert not settings.get("library.width").is_default()
    settings.reset()
    assert settings.get("library.width").is_default()
