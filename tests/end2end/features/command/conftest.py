# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""bdd steps for testing commands."""

import os

from PyQt5.QtCore import QThreadPool

import pytest_bdd as bdd


@bdd.when("I wait for the command to complete")
def wait_for_external_command(qtbot):
    """Wait until the external process has completed."""
    max_iterations = 100
    iteration = 0
    while (
        QThreadPool.globalInstance().activeThreadCount() and iteration < max_iterations
    ):
        qtbot.wait(10)
        iteration += 1
    assert iteration != max_iterations, "external command timed out"


@bdd.then(bdd.parsers.parse("the file {name} should exist"))
def check_file_exists(name):
    assert os.path.isfile(name)


@bdd.then(bdd.parsers.parse("the file {name} should not exist"))
def check_not_file_exists(name):
    assert not os.path.isfile(name)


@bdd.then(bdd.parsers.parse("the directory {name} should exist"))
def check_directory_exists(name):
    assert os.path.isdir(name)


@bdd.then(bdd.parsers.parse("the directory {name} should not exist"))
def check_not_directory_exists(name):
    assert not os.path.isdir(name)
