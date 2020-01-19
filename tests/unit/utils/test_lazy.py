# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.lazy."""

import pytest

from vimiv.utils import lazy

MODULE_NAME = "_module_for_lazy"


@pytest.fixture(autouse=True)
def clear_lazy_lru_cache():
    """Fixture to clean the module lru_cache after every test."""
    yield
    lazy.Module.factory.cache_clear()


@pytest.fixture()
def module():
    """Fixture to return a lazy imported module."""
    yield lazy.import_module(MODULE_NAME)


def test_lazy_import_is_lazy(module, capsys):
    """Ensure the module is not executed upon import."""
    captured = capsys.readouterr()
    assert MODULE_NAME not in captured.out


def test_lazy_imported_module(module, capsys):
    """Ensure the module works as expected when used."""
    assert module.function_of_interest() == module.RETURN_VALUE
    captured = capsys.readouterr()
    assert MODULE_NAME in captured.out


def test_lazy_module_single_instance(module):
    """Ensure we only create a single instance per module name."""
    module_second_import = lazy.import_module(MODULE_NAME)
    assert module_second_import is module
