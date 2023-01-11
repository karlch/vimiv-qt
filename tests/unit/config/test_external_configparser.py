# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Unit tests for vimiv.config.external_configparser."""

import collections
import configparser

import pytest

from vimiv.config import external_configparser


ENV_VARIABLE = collections.namedtuple("EnvironmentVariable", ["name", "value"])(
    "COLOR0", "#121212"
)
SECTION_NAME = "default".upper()
OPTION_NAME = ENV_VARIABLE.name.lower()


@pytest.fixture()
def parser():
    yield external_configparser.get_parser()


@pytest.fixture()
def config(tmp_path):
    """Fixture to retrieve a written config file with external references."""
    parser = configparser.ConfigParser()
    parser[SECTION_NAME][OPTION_NAME] = "${env:" + ENV_VARIABLE.name + "}"
    path = tmp_path / "config.ini"
    with open(path, "w", encoding="utf-8") as f:
        parser.write(f)
    yield str(path)


@pytest.fixture()
def setup_env(monkeypatch):
    """Fixture to add and clean up an environment variable."""
    variable, value = ENV_VARIABLE
    monkeypatch.setenv(variable, value)


@pytest.mark.parametrize(
    "pattern, expected",
    [
        ("${test}", "test"),
        ("${}", ""),
        ("${", None),
        ("$}", None),
        ("$(anything)", None),
    ],
)
def test_variable_match_regex(pattern, expected):
    match = external_configparser.VARIABLE_RE.match(pattern)
    if match is None:
        assert expected is None
    else:
        assert match.group(0) == "${" + expected + "}"
        assert match.group(1) == expected


def test_update_variable_from_env(setup_env):
    variable, expected = ENV_VARIABLE
    option = "${env:" + variable + "}"
    assert external_configparser.ExternalInterpolation.update(option) == expected


@pytest.mark.parametrize("variable", ["", ":", ":test", "something:test"])
def test_fail_update_variable_invalid_prefix(variable):
    with pytest.raises(configparser.Error, match="Invalid variable name"):
        external_configparser.ExternalInterpolation.update("${" + variable + "}")


def test_fail_update_variable_from_env():
    with pytest.raises(configparser.Error, match="not found in environment"):
        external_configparser.ExternalInterpolation.update("${env:not_in_env}")


def test_read_env_variable_from_config(setup_env, config, parser):
    parser.read(config)
    assert parser.get(SECTION_NAME, OPTION_NAME) == ENV_VARIABLE.value
