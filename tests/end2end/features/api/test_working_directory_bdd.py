# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2022 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("working_directory.feature")


@bdd.then(bdd.parsers.parse("there should be {n_directories:d} monitored directory"))
@bdd.then(bdd.parsers.parse("there should be {n_directories:d} monitored directories"))
def check_monitored_directories(n_directories):
    assert len(api.working_directory.handler.directories()) == n_directories


@bdd.then(bdd.parsers.parse("there should be {n_files:d} monitored file"))
@bdd.then(bdd.parsers.parse("there should be {n_files:d} monitored files"))
def check_monitored_files(n_files):
    assert len(api.working_directory.handler.files()) == n_files
