# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import logging

import pytest_bdd as bdd

import vimiv
from vimiv.utils import log


bdd.scenarios("startup.feature")


@bdd.then("the version information should be displayed")
def check_version_information(run_vimiv_version):
    assert vimiv.__name__ in run_vimiv_version
    assert vimiv.__version__ in run_vimiv_version


@bdd.then("the log level should be <level>")
def check_log_level(level):
    loglevel = getattr(logging, level.upper())
    assert log._app_logger.level == loglevel
