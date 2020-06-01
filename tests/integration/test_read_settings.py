# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Integration tests related to reading settings from configuration file."""

import pytest

from vimiv import api
from vimiv.commands import aliases
from vimiv.config import configfile


########################################################################################
#        Configuration dictionaries used to parametrize the configuration file         #
########################################################################################
UPDATED_CONFIG = {
    "GENERAL": {"shuffle": "True"},
    "IMAGE": {"overzoom": "4.2"},
    "THUMBNAIL": {"size": "64"},
}


UPDATED_STATUSBAR = {
    "STATUSBAR": {
        "center_image": "value",
        "left_image": "value",
        "left_thumbnail": "value",
        "right": "value",
        "right_image": "value",
    }
}


UPDATED_CONFIG_INVALID = {
    "GENERAL": {"shuffle": "not a bool"},
    "IMAGE": {"overzoom": "not a float"},
    "THUMBNAIL": {"size": "not an int"},
}


########################################################################################
#                                      Fixtures                                        #
########################################################################################
@pytest.fixture(autouse=True)
def reset_to_default(cleanup_helper):
    """Fixture to ensure everything is reset to default after testing."""
    yield from cleanup_helper(aliases._aliases)
    api.settings.reset()


@pytest.fixture(scope="function")
def configpath(tmpdir, custom_configfile, request):
    yield custom_configfile(
        "vimiv.conf", configfile.read, configfile.get_default_parser, **request.param
    )


@pytest.fixture()
def mock_strsetting(mocker):
    yield mocker.patch.object(api.settings, "StrSetting")


@pytest.fixture()
def mock_logger(mocker):
    yield mocker.patch.object(configfile, "_logger")


########################################################################################
#                                        Tests                                         #
########################################################################################
@pytest.mark.parametrize("configpath", [UPDATED_CONFIG], indirect=["configpath"])
def test_read_config(configpath):
    """Ensure updated settings are read correctly."""
    assert api.settings.shuffle.value is True
    assert api.settings.image.overzoom.value == 4.2
    assert api.settings.thumbnail.size.value == 64


@pytest.mark.parametrize(
    "configpath", [{"ALIASES": {"anything": "scroll left"}}], indirect=["configpath"]
)
def test_read_aliases(configpath):
    """Ensure new aliases are read correctly."""
    global_aliases = aliases.get(api.modes.IMAGE)
    assert "anything" in global_aliases
    assert global_aliases["anything"] == "scroll left"


@pytest.mark.parametrize("configpath", [UPDATED_STATUSBAR], indirect=["configpath"])
def test_read_statusbar_formatters(mock_strsetting, configpath):
    """Ensure various statusbar formatters are read correctly."""
    for name, value in UPDATED_STATUSBAR["STATUSBAR"].items():
        setting_name = f"statusbar.{name}"
        if "_" in name:  # Optional mode dependent formatter
            mock_strsetting.assert_any_call(setting_name, value)
        else:  # Changed existing global setting
            assert api.settings.get_value(setting_name) == value


@pytest.mark.parametrize(
    "configpath", [UPDATED_CONFIG_INVALID], indirect=["configpath"]
)
def test_read_invalid_setting(mock_logger, configpath):
    """Ensure settings with invalid values log appropriate error messages."""
    # Build set of all setting names with invalid values
    setting_names = {
        key if section == "GENERAL" else f"{section.lower()}.{key}"
        for section, content in UPDATED_CONFIG_INVALID.items()
        for key in content
    }
    # Ensure an error was logged for each of the settings
    for _, args, _ in mock_logger.error.mock_calls:
        assert set(args) & setting_names
    # Ensure all settings are at default value
    for name in setting_names:
        setting = api.settings.get(name)
        assert setting.value == setting.default
