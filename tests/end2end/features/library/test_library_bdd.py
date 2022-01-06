# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2022 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd


bdd.scenarios("library.feature")


@bdd.when("I reload the library")
def reload_library(library):
    library._open_directory(".", reload_current=True)


@bdd.then(bdd.parsers.parse("the library should contain {n_paths:d} paths"))
def check_library_paths(library, n_paths):
    assert len(library.pathlist()) == n_paths
