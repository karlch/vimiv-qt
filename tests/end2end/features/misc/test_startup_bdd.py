# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import logging

import pytest_bdd as bdd

import vimiv
from vimiv.utils import log


bdd.scenarios("startup.feature")


@bdd.then("the version information should be displayed")
def check_version_information(output):
    assert vimiv.__name__ in output.out
    assert vimiv.__version__ in output.out


@bdd.then(bdd.parsers.parse("the log level should be {level}"))
def check_log_level(level):
    loglevel = getattr(logging, level.upper())
    assert log._app_logger.level == loglevel
