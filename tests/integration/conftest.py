# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Common fixtures for integration testing."""

import pytest


@pytest.fixture()
def custom_configparser():
    """Fixture to create a custom configparser adding to defaults."""

    def create_custom_parser(default_parser, **sections):
        parser = default_parser()
        for section, content in sections.items():
            for key, value in content.items():
                parser[section][key] = value
        return parser

    return create_custom_parser


@pytest.fixture()
def custom_configfile(tmp_path, custom_configparser):
    """Fixture to create a custom config file from a configparser."""

    def create_custom_configfile(basename, read, default_parser, **sections):
        parser = custom_configparser(default_parser, **sections)
        path = tmp_path / basename
        with open(path, "w", encoding="utf-8") as f:
            parser.write(f)
        read(str(path))

    return create_custom_configfile
