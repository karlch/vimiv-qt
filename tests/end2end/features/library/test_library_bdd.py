# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os
import pytest_bdd as bdd


bdd.scenarios("library.feature")


@bdd.when("I add a hidden path")
def add_hidden_path():
    os.mkdir(".hidden_directory")


@bdd.when("I reload the library")
def reload_library(library):
    library._open_directory(".", reload_current=True)


@bdd.then(bdd.parsers.parse("the library should contain {n_paths:d} paths"))
def check_library_paths(library, n_paths):
    assert len(library.pathlist()) == n_paths
