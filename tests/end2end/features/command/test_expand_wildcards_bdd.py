# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest
import pytest_bdd as bdd


bdd.scenarios("expand_wildcards.feature")


@pytest.fixture(autouse=True)
def home_directory(tmp_path, mocker):
    """Fixture to mock os.path.expanduser to return a different home directory."""
    directory = tmp_path / "home"
    directory.mkdir()
    new_home = str(directory)

    def expand_user(path):
        return path.replace("~", new_home)

    mocker.patch("os.path.expanduser", new=expand_user)
    yield new_home


@bdd.then(bdd.parsers.parse("the home directory should contain {path}"))
def check_path_in_home(home_directory, path):
    assert path in os.listdir(home_directory)
