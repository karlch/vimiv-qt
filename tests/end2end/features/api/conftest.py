# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import os

import pytest_bdd as bdd

from vimiv import api


@bdd.then(bdd.parsers.parse("there should be {n_marked:d} marked images"))
def check_number_marked(n_marked):
    assert len(api.mark.paths) == n_marked


@bdd.then(bdd.parsers.parse("{path} should be marked"))
def check_image_marked(path):
    assert path in [os.path.basename(p) for p in api.mark.paths]


@bdd.then(bdd.parsers.parse("{path} should not be marked"))
def check_image_not_marked(path):
    assert path not in [os.path.basename(p) for p in api.mark.paths]
