# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest_bdd as bdd


bdd.scenarios("external.feature")


@bdd.when("I wait for the command to complete")
def wait_for_external_command(qtbot):
    """Just wait for a short time as tests should run fast commands."""
    qtbot.wait(10)


@bdd.then(bdd.parsers.parse("the file {name} should exist"))
def check_file_exists(name):
    assert os.path.isfile(name)
